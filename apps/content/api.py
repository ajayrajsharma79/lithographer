from rest_framework import serializers
from django.utils.translation import get_language, gettext_lazy as _
from django.db import transaction
from django.conf import settings

from .models import (
    ContentType, FieldDefinition, Taxonomy, Term,
    ContentInstance, ContentFieldInstance, ContentVersion
)
# Import serializers from other apps if needed (e.g., for user/language)
from apps.core.models import Language
from apps.users.api import CMSUserSerializer
# Import component models for layout data
from apps.components.models import PageComponent

# --- Content Type & Field Definition Serializers (Read-Only for now) ---

class FieldDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for FieldDefinition (nested within ContentType)."""
    class Meta:
        model = FieldDefinition
        fields = ['id', 'name', 'api_id', 'field_type', 'order', 'config', 'is_localizable', 'is_required']
        read_only_fields = fields # Read-only via this nested serializer


class ContentTypeSerializer(serializers.ModelSerializer):
    """Serializer for ContentType (Read-Only)."""
    field_definitions = FieldDefinitionSerializer(many=True, read_only=True)

    class Meta:
        model = ContentType
        fields = ['id', 'name', 'api_id', 'description', 'field_definitions', 'created_at', 'updated_at']
        read_only_fields = fields


# --- Taxonomy & Term Serializers ---

class TermSerializer(serializers.ModelSerializer):
    """Serializer for Taxonomy Terms."""
    taxonomy_api_id = serializers.SlugRelatedField(
        source='taxonomy', read_only=True, slug_field='api_id'
    )
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Term.objects.all(), # Queryset filtered in validation/view
        source='parent', allow_null=True, required=False
    )
    # Expose translated fields directly for current language? Or keep as JSON?
    # Keeping as JSON for full control via API for now.
    # name = serializers.SerializerMethodField()
    # slug = serializers.SerializerMethodField()

    class Meta:
        model = Term
        fields = [
            'id', 'taxonomy', 'taxonomy_api_id', 'parent_id',
            'translated_names', 'translated_slugs',
            'created_at', 'updated_at'
            # 'name', 'slug' # If using SerializerMethodField
        ]
        read_only_fields = ['id', 'taxonomy_api_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'taxonomy': {'write_only': True}, # Set via URL or explicit field
        }

    # def get_name(self, obj):
    #     return obj.get_name(get_language()) # Get name in current request language

    # def get_slug(self, obj):
    #     return obj.get_slug(get_language()) # Get slug in current request language

    def validate(self, data):
        # Validate parent assignment based on taxonomy hierarchy
        taxonomy = data.get('taxonomy', getattr(self.instance, 'taxonomy', None))
        parent = data.get('parent', getattr(self.instance, 'parent', None))

        if not taxonomy:
             # This should typically be enforced by the viewset based on URL
             raise serializers.ValidationError({"taxonomy": _("Taxonomy must be specified.")})

        if parent:
            if not taxonomy.hierarchical:
                raise serializers.ValidationError({"parent": _("Cannot assign parent in a non-hierarchical taxonomy.")})
            if parent.taxonomy != taxonomy:
                raise serializers.ValidationError({"parent": _("Parent term must belong to the same taxonomy.")})
            # Prevent self-assignment or circular references (basic check)
            if self.instance and parent.pk == self.instance.pk:
                 raise serializers.ValidationError({"parent": _("Term cannot be its own parent.")})
            # Add more robust circular reference check if needed (e.g., checking ancestors)

        # Validate translated_names and translated_slugs structure if needed
        # Ensure keys are valid language codes?

        return data


class TaxonomySerializer(serializers.ModelSerializer):
    """Serializer for Taxonomies."""
    content_types_api_ids = serializers.SlugRelatedField(
        source='content_types',
        queryset=ContentType.objects.all(),
        slug_field='api_id',
        many=True,
        required=False
    )
    # Optionally include nested terms (can be large)
    # terms = TermSerializer(many=True, read_only=True)

    class Meta:
        model = Taxonomy
        fields = [
            'id', 'name', 'api_id', 'hierarchical',
            'content_types', 'content_types_api_ids',
            'created_at', 'updated_at'
            # 'terms' # If including nested terms
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'content_types': {'write_only': True}, # Use api_ids field for input/output
        }


# --- Content Instance Serializers (Complex) ---

class ContentFieldInstanceSerializer(serializers.ModelSerializer):
    """
    Internal serializer for ContentFieldInstance.
    Used primarily for representing data within ContentInstanceSerializer.
    Direct API manipulation of these might be disabled.
    """
    field_api_id = serializers.SlugRelatedField(source='field_definition', read_only=True, slug_field='api_id')
    language_code = serializers.SlugRelatedField(source='language', read_only=True, slug_field='code')

    class Meta:
        model = ContentFieldInstance
        fields = ['id', 'field_definition', 'field_api_id', 'language', 'language_code', 'value']
        read_only_fields = ['id', 'field_api_id', 'language_code']


# --- Page Component Serializer (for nested layout data) ---
class PageComponentSerializer(serializers.ModelSerializer):
    """Read-only serializer for representing PageComponent data in layouts."""
    component_api_id = serializers.SlugRelatedField(
        source='component_definition', read_only=True, slug_field='api_id'
    )

    class Meta:
        model = PageComponent
        fields = ['id', 'component_api_id', 'order', 'data']
        read_only_fields = fields


class ContentInstanceSerializer(serializers.ModelSerializer):
    """
    Serializer for ContentInstance. Handles dynamic fields based on ContentType.
    """
    content_type_api_id = serializers.SlugRelatedField(
        source='content_type', read_only=True, slug_field='api_id'
    )
    author_detail = CMSUserSerializer(source='author', read_only=True)
    # Use PrimaryKeyRelatedField for setting terms on write
    term_ids = serializers.PrimaryKeyRelatedField(
        source='terms', queryset=Term.objects.all(), many=True, write_only=True, required=False
    )
    # Represent terms with more detail on read
    terms_detail = TermSerializer(source='terms', many=True, read_only=True)

    # Dynamic field handling: Use a dictionary for input/output
    # Structure: {"lang_code": {"field_api_id": value, ...}, "non_localizable": {"field_api_id": value, ...}}
    # Or simpler: {"field_api_id": value} for non-localizable, {"field_api_id": {"lang_code": value, ...}} for localizable
    # Let's try the simpler approach for input/output representation:
    content_data = serializers.SerializerMethodField(read_only=True) # Renamed from 'fields'
    # Add field for layout components
    layout_components = PageComponentSerializer(
        source='components', # Use the related name from ContentInstance to PageComponent FK
        many=True,
        read_only=True
    )
    # For write operations, we'll expect a similar structure in request.data['content_data']
    # Layout component data is saved via the admin inline for now.

    class Meta:
        model = ContentInstance
        fields = [
            'id', 'content_type', 'content_type_api_id', 'status',
            'author', 'author_detail', 'created_at', 'updated_at', 'published_at',
            'terms', 'term_ids', 'terms_detail',
            'content_data', # Renamed from 'fields'
            'layout_components' # Added layout data
        ]
        read_only_fields = [
            'id', 'content_type_api_id', 'author_detail', 'terms_detail',
            'created_at', 'updated_at', 'published_at', 'content_data', # Renamed from 'fields'
            'layout_components' # Layout is read-only via this serializer
        ]
        extra_kwargs = {
            'content_type': {'write_only': True, 'required': True}, # Required on create
            'author': {'write_only': True, 'required': False}, # Set automatically
            'terms': {'write_only': True}, # Use term_ids for input
        }

    def get_content_data(self, obj): # Renamed from get_fields
        """
        Retrieve and structure field data for output, applying language fallback.
        """
        # Determine requested language and fallbacks
        request = self.context.get('request')
        requested_lang_code = request.query_params.get('lang') if request else None
        if not requested_lang_code:
            requested_lang_code = settings.LANGUAGE_CODE # Site default

        base_lang_code = requested_lang_code.split('-')[0]
        site_default_lang_code = settings.LANGUAGE_CODE
        fallback_order = [requested_lang_code]
        if base_lang_code != requested_lang_code:
            fallback_order.append(base_lang_code)
        if site_default_lang_code not in fallback_order:
             fallback_order.append(site_default_lang_code)
        # Add base of site default if different
        site_default_base = site_default_lang_code.split('-')[0]
        if site_default_base not in fallback_order:
            fallback_order.append(site_default_base)


        structured_fields = {}
        # Optimize: Fetch all field instances at once
        field_instances = obj.field_instances.select_related('field_definition', 'language').all()
        # Group instances by field definition API ID and language code
        instances_map = {} # { "field_api_id": { "lang_code": value, ... }, ... }
        non_localizable_map = {} # { "field_api_id": value }

        for fi in field_instances:
            api_id = fi.field_definition.api_id
            if fi.language: # Localizable
                if api_id not in instances_map:
                    instances_map[api_id] = {}
                instances_map[api_id][fi.language.code] = fi.value
            else: # Non-localizable
                non_localizable_map[api_id] = fi.value

        # Iterate through definitions to ensure all fields are considered
        definitions = obj.content_type.field_definitions.all()
        for definition in definitions:
            api_id = definition.api_id
            if definition.is_localizable:
                found_value = None
                found_lang_code = None
                # Try fallbacks in order
                lang_values = instances_map.get(api_id, {})
                for lang_code in fallback_order:
                    if lang_code in lang_values:
                        found_value = lang_values[lang_code]
                        found_lang_code = lang_code
                        break
                # Final fallback: first available language for this field
                if found_value is None and lang_values:
                     first_lang = next(iter(lang_values.keys()))
                     found_value = lang_values[first_lang]
                     found_lang_code = first_lang

                # Structure output to include value and language it came from
                if found_value is not None:
                     structured_fields[api_id] = {
                         "value": found_value,
                         "language": found_lang_code
                     }
                else:
                     structured_fields[api_id] = None # Or {"value": None, "language": None}

            else:
                # Non-localizable field
                structured_fields[api_id] = non_localizable_map.get(api_id) # Value is directly stored

        return structured_fields

    @transaction.atomic
    def create(self, validated_data):
        """Handle creation of ContentInstance and its ContentFieldInstances."""
        term_data = validated_data.pop('terms', None) # Use term_ids source
        # Get content_data from raw request data (key should match input structure)
        content_input_data = self.context['request'].data.get('content_data', {})
        validated_data['author'] = self.context['request'].user # Set author

        instance = super().create(validated_data)

        self._save_field_instances(instance, content_input_data) # Pass renamed data

        if term_data is not None:
            instance.terms.set(term_data)

        # Optionally create initial version
        ContentVersion.create_version(instance, user=instance.author, message="Initial creation")

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        """Handle update of ContentInstance and its ContentFieldInstances."""
        term_data = validated_data.pop('terms', None) # Use term_ids source
        # Get content_data if provided in the update request
        content_input_data = self.context['request'].data.get('content_data', None)

        # Prevent changing content_type after creation
        validated_data.pop('content_type', None)
        # Author should generally not be changed on update
        validated_data.pop('author', None)

        # Track if status changes to published
        original_status = instance.status
        instance = super().update(instance, validated_data)
        new_status = instance.status

        if content_input_data is not None:
            # Option 1: Replace all fields (simpler, but destructive)
            # instance.field_instances.all().delete()
            # self._save_field_instances(instance, content_input_data)
            # Option 2: Update existing/create new (more complex, preserves IDs)
            self._update_field_instances(instance, content_input_data) # Pass renamed data


        if term_data is not None:
            instance.terms.set(term_data)

        # Create new version on significant changes (e.g., status change, or if fields updated)
        # More sophisticated logic might be needed (e.g., debounce, check for actual data change)
        create_new_version = False
        if new_status != original_status:
             create_new_version = True
             # If changing to published, update published_at (handled by model save)
        if content_input_data is not None: # Assume field update means version change for now
             create_new_version = True

        if create_new_version:
             # TODO: Get user performing the update (might not be request.user if using API key?)
             user = self.context['request'].user if self.context['request'].user.is_authenticated else None
             ContentVersion.create_version(instance, user=user, message="Content updated")


        return instance

    def _save_field_instances(self, instance, content_input_data): # Renamed parameter
        """Helper to create ContentFieldInstance objects from structured data."""
        definitions = instance.content_type.field_definitions.all()
        def_map = {d.api_id: d for d in definitions}
        active_languages = Language.objects.filter(is_active=True)
        lang_map = {l.code: l for l in active_languages}

        instances_to_create = []
        for api_id, value_data in content_input_data.items(): # Use renamed parameter
            definition = def_map.get(api_id)
            if not definition: continue # Ignore data for unknown fields

            if definition.is_localizable:
                if isinstance(value_data, dict):
                    for lang_code, value in value_data.items():
                        language = lang_map.get(lang_code)
                        if not language: continue # Ignore data for inactive languages
                        # TODO: Add validation based on definition.field_type
                        instances_to_create.append(ContentFieldInstance(
                            content_instance=instance,
                            field_definition=definition,
                            language=language,
                            value=value
                        ))
            else:
                # TODO: Add validation based on definition.field_type
                instances_to_create.append(ContentFieldInstance(
                    content_instance=instance,
                    field_definition=definition,
                    language=None,
                    value=value_data
                ))

        if instances_to_create:
            ContentFieldInstance.objects.bulk_create(instances_to_create)

    def _update_field_instances(self, instance, content_input_data): # Renamed parameter
         """Helper to update/create ContentFieldInstance objects (more complex)."""
         definitions = instance.content_type.field_definitions.all()
         def_map = {d.api_id: d for d in definitions}
         active_languages = Language.objects.filter(is_active=True)
         lang_map = {l.code: l for l in active_languages}
         existing_fis = instance.field_instances.all()
         fi_map = {} # {(field_def_id, lang_id_or_None): fi_instance}
         for fi in existing_fis:
             fi_map[(fi.field_definition_id, getattr(fi.language, 'pk', None))] = fi

         instances_to_update = []
         instances_to_create = []

         for api_id, value_data in content_input_data.items(): # Use renamed parameter
             definition = def_map.get(api_id)
             if not definition: continue

             if definition.is_localizable:
                 if isinstance(value_data, dict):
                     for lang_code, value in value_data.items():
                         language = lang_map.get(lang_code)
                         if not language: continue
                         # TODO: Add validation
                         key = (definition.pk, language.pk)
                         if key in fi_map:
                             fi = fi_map[key]
                             if fi.value != value: # Only update if changed
                                 fi.value = value
                                 instances_to_update.append(fi)
                         else:
                             instances_to_create.append(ContentFieldInstance(
                                 content_instance=instance, field_definition=definition, language=language, value=value
                             ))
             else:
                 # TODO: Add validation
                 key = (definition.pk, None)
                 if key in fi_map:
                     fi = fi_map[key]
                     if fi.value != value_data: # Only update if changed
                         fi.value = value_data
                         instances_to_update.append(fi)
                 else:
                     instances_to_create.append(ContentFieldInstance(
                         content_instance=instance, field_definition=definition, language=None, value=value_data
                     ))

         if instances_to_create:
             ContentFieldInstance.objects.bulk_create(instances_to_create)
         if instances_to_update:
             # Note: bulk_update might not trigger signals if needed later
             ContentFieldInstance.objects.bulk_update(instances_to_update, ['value'])

         # TODO: Optionally delete field instances that were present before but are not in fields_data?


class ContentVersionSerializer(serializers.ModelSerializer):
    """Serializer for ContentVersion (Read-Only)."""
    content_instance_id = serializers.UUIDField(source='content_instance.id', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True, allow_null=True)

    class Meta:
        model = ContentVersion
        fields = [
            'id', 'content_instance_id', 'data_snapshot', 'status_snapshot',
            'version_message', 'created_by_email', 'created_at'
        ]
        read_only_fields = fields