from rest_framework import serializers
from apps.organizations.models import Organization, Project, Membership
from apps.authentication.models import User

class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Membership
        fields = ('id', 'user', 'user_email', 'user_full_name', 'organization', 'role', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

class OrganizationSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(source='memberships.count', read_only=True)
    my_role = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ('id', 'name', 'slug', 'plan_type', 'settings', 'is_active', 'member_count', 'my_role', 'created_at')
        read_only_fields = ('id', 'slug', 'created_at')

    def get_my_role(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        membership = obj.memberships.filter(user=request.user, is_active=True).first()
        return membership.role if membership else None

class ProjectSerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(source='assets.count', read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'organization', 'name', 'description', 'is_active', 'asset_count', 'created_at')
        read_only_fields = ('id', 'created_at')

class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(choices=Membership.OrgRole.choices, default=Membership.OrgRole.DEVELOPER)
