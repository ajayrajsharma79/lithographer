# Generated by Django 5.2 on 2025-04-18 07:11

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text="Human-readable name (e.g., 'Blog Post').", max_length=100, unique=True, verbose_name='Content Type Name')),
                ('api_id', models.SlugField(help_text="Unique identifier used in APIs and code (e.g., 'blog_post'). Automatically generated if left blank.", max_length=100, unique=True, verbose_name='API ID')),
                ('description', models.TextField(blank=True, help_text='Optional description of this content type.', verbose_name='Description')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Content Type',
                'verbose_name_plural': 'Content Types',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='FieldDefinition',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text="Human-readable name for the field (e.g., 'Post Title').", max_length=100, verbose_name='Field Name')),
                ('api_id', models.SlugField(help_text="Unique identifier for the field within the Content Type (e.g., 'post_title'). Automatically generated if left blank.", max_length=100, verbose_name='API ID')),
                ('field_type', models.CharField(choices=[('text', 'Text (Single Line)'), ('rich_text', 'Rich Text (Multi Line)'), ('number', 'Number (Integer/Float)'), ('date', 'Date/DateTime'), ('boolean', 'Boolean (True/False)'), ('email', 'Email Address'), ('url', 'URL'), ('media', 'Media (Link to Media Library)'), ('relationship', 'Relationship (Link to other Content Instance)'), ('select', 'Select (Dropdown/Radio)'), ('structured_list', 'Structured List (Repeater)'), ('json', 'JSON')], help_text='Determines the kind of data stored and the input widget used.', max_length=50, verbose_name='Field Type')),
                ('order', models.PositiveIntegerField(default=0, help_text='Order in which fields appear in the admin interface.', verbose_name='Order')),
                ('config', models.JSONField(blank=True, default=dict, help_text="Field-specific settings (JSON format). Keys include: 'required' (bool), 'unique' (bool, requires careful implementation), 'default_value', 'help_text' (str), 'validation_rules' (e.g., min_length, max_length, regex), 'localizable' (bool), 'select_options' (list for 'select' type), 'allowed_content_types' (list of api_ids for 'relationship' type), 'allowed_media_types' (list for 'media' type).", verbose_name='Configuration')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='field_definitions', to='content.contenttype', verbose_name='Content Type')),
            ],
            options={
                'verbose_name': 'Field Definition',
                'verbose_name_plural': 'Field Definitions',
                'ordering': ['content_type', 'order', 'name'],
                'unique_together': {('content_type', 'api_id')},
            },
        ),
        migrations.CreateModel(
            name='Taxonomy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text="Human-readable name (e.g., 'Categories').", max_length=100, unique=True, verbose_name='Taxonomy Name')),
                ('api_id', models.SlugField(help_text="Unique identifier for API use (e.g., 'categories'). Automatically generated.", max_length=100, unique=True, verbose_name='API ID')),
                ('hierarchical', models.BooleanField(default=False, help_text='Does this taxonomy support parent-child relationships (like categories)?', verbose_name='Hierarchical')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content_types', models.ManyToManyField(blank=True, help_text='Content types that can use this taxonomy.', related_name='taxonomies', to='content.contenttype', verbose_name='Applicable Content Types')),
            ],
            options={
                'verbose_name': 'Taxonomy',
                'verbose_name_plural': 'Taxonomies',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('translated_names', models.JSONField(default=dict, help_text="Term names in different languages (JSON format: {'lang_code': 'Name'}).", verbose_name='Translated Names')),
                ('translated_slugs', models.JSONField(default=dict, help_text="Term slugs in different languages (JSON format: {'lang_code': 'slug'}).", verbose_name='Translated Slugs')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(blank=True, help_text='Used for hierarchical taxonomies.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='content.term', verbose_name='Parent Term')),
                ('taxonomy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terms', to='content.taxonomy', verbose_name='Taxonomy')),
            ],
            options={
                'verbose_name': 'Term',
                'verbose_name_plural': 'Terms',
                'ordering': ['taxonomy', 'translated_names'],
            },
        ),
        migrations.CreateModel(
            name='ContentInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('in_review', 'In Review'), ('published', 'Published'), ('rejected', 'Rejected'), ('archived', 'Archived')], db_index=True, default='draft', max_length=20, verbose_name='Status')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_at', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Published At')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='content_instances', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='instances', to='content.contenttype', verbose_name='Content Type')),
                ('terms', models.ManyToManyField(blank=True, help_text='Terms associated with this content instance.', related_name='content_instances', to='content.term', verbose_name='Taxonomy Terms')),
            ],
            options={
                'verbose_name': 'Content Instance',
                'verbose_name_plural': 'Content Instances',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='ContentVersion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('data_snapshot', models.JSONField(help_text='Snapshot of content field instance data for this version.', verbose_name='Data Snapshot')),
                ('status_snapshot', models.CharField(choices=[('draft', 'Draft'), ('in_review', 'In Review'), ('published', 'Published'), ('rejected', 'Rejected'), ('archived', 'Archived')], max_length=20, verbose_name='Status Snapshot')),
                ('version_message', models.TextField(blank=True, help_text='Optional message describing the changes in this version.', verbose_name='Version Message')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Version Created At')),
                ('content_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='content.contentinstance', verbose_name='Content Instance')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
            ],
            options={
                'verbose_name': 'Content Version',
                'verbose_name_plural': 'Content Versions',
                'ordering': ['content_instance', '-created_at'],
                'indexes': [models.Index(fields=['content_instance', '-created_at'], name='content_con_content_1c2629_idx')],
            },
        ),
        migrations.CreateModel(
            name='ContentFieldInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('value', models.JSONField(blank=True, help_text='The actual data stored for this field instance.', null=True, verbose_name='Value')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('language', models.ForeignKey(blank=True, help_text='Language for this field value (null if field is not localizable).', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.language', verbose_name='Language')),
                ('content_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='field_instances', to='content.contentinstance', verbose_name='Content Instance')),
                ('field_definition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='content.fielddefinition', verbose_name='Field Definition')),
            ],
            options={
                'verbose_name': 'Content Field Instance',
                'verbose_name_plural': 'Content Field Instances',
                'ordering': ['content_instance', 'field_definition__order'],
                'indexes': [models.Index(fields=['content_instance', 'field_definition', 'language'], name='content_con_content_5ad471_idx')],
                'unique_together': {('content_instance', 'field_definition', 'language')},
            },
        ),
    ]
