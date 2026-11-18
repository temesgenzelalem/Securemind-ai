from rest_framework import serializers
from apps.audit.models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source='actor.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = ('id', 'organization', 'actor', 'actor_email', 'action', 'target_type', 'target_id', 'ip_address', 'details', 'created_at')
        read_only_fields = fields
