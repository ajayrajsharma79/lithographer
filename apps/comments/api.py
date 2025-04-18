from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import Comment, STATUS_PENDING
from apps.frontend_users.api import FrontEndUserSerializer # To show user details

class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comments."""
    # Use nested serializer for user details on read
    user_detail = FrontEndUserSerializer(source='user', read_only=True)
    # Allow setting parent via ID on write
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(), # Queryset potentially filtered in view/validation
        source='parent', allow_null=True, required=False, write_only=True
    )
    # Content instance is set via URL, not directly in payload
    content_instance = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'content_instance', 'user', 'user_detail', 'parent', 'parent_id',
            'body', 'status', 'submission_timestamp'
        ]
        read_only_fields = [
            'id', 'content_instance', 'user', 'user_detail', 'parent', # Parent shown nested on read if needed
            'status', 'submission_timestamp'
        ]
        extra_kwargs = {
            'body': {'required': True},
        }

    def validate_parent_id(self, value):
        """Ensure parent comment belongs to the same content instance."""
        if value: # If parent_id is provided
            content_instance_pk = self.context['view'].kwargs.get('instance_pk')
            if not content_instance_pk:
                 # Should not happen if URL is correct
                 raise serializers.ValidationError(_("Could not determine Content Instance from context."))
            if value.content_instance_id != content_instance_pk:
                raise serializers.ValidationError(_("Parent comment must belong to the same content instance."))
        return value

    def create(self, validated_data):
         # Set user and content_instance from context provided by the view
        validated_data['user'] = self.context['request'].user
        validated_data['content_instance_id'] = self.context['view'].kwargs['instance_pk']
        # Comments start as pending
        validated_data['status'] = STATUS_PENDING
        return super().create(validated_data)


class ReadCommentSerializer(serializers.ModelSerializer):
     """
     Read-only serializer for comments, potentially including replies.
     Used for embedding comments in content API responses.
     """
     user_display = serializers.CharField(source='user.display_name', read_only=True)
     # Use a recursive serializer for replies
     replies = serializers.SerializerMethodField(read_only=True)

     class Meta:
         model = Comment
         fields = [
             'id', 'user_display', 'parent', # Include parent ID for client-side threading
             'body', 'submission_timestamp', 'replies'
         ]

     def get_replies(self, obj):
         # Only include approved replies
         approved_replies = obj.replies.filter(status=STATUS_APPROVED)
         # Limit depth or use pagination if nesting can be deep
         serializer = ReadCommentSerializer(approved_replies, many=True, read_only=True, context=self.context)
         return serializer.data