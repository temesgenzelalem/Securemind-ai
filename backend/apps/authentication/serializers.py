from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from apps.authentication.models import User
from apps.organizations.models import Organization, Membership

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that embeds role, full name, and active organization context.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        if user.current_organization:
            token['org_id'] = str(user.current_organization.id)
            token['org_name'] = user.current_organization.name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'role': self.user.role,
            'full_name': self.user.full_name,
            'current_organization': {
                'id': str(self.user.current_organization.id),
                'name': self.user.current_organization.name,
                'slug': self.user.current_organization.slug
            } if self.user.current_organization else None
        }
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    organization_name = serializers.CharField(write_only=True, required=False, default="")

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'role', 'organization_name', 'created_at')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        org_name = validated_data.pop('organization_name', '').strip()
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        # Create default organization for new user if not specified
        if not org_name:
            org_name = f"{user.first_name}'s Workspace" if user.first_name else f"{user.email.split('@')[0]}'s Workspace"

        base_slug = slugify(org_name) or 'workspace'
        unique_slug = f"{base_slug}-{str(user.id)[:8]}"
        
        organization = Organization.objects.create(
            name=org_name,
            slug=unique_slug,
            created_by=user
        )

        # Set user as Admin of their created organization
        Membership.objects.create(
            user=user,
            organization=organization,
            role=Membership.OrgRole.ADMIN
        )

        user.current_organization = organization
        user.save(update_fields=['current_organization'])

        return user

class UserProfileSerializer(serializers.ModelSerializer):
    current_organization_name = serializers.CharField(source='current_organization.name', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'is_active', 'is_verified', 'current_organization',
            'current_organization_name', 'created_at'
        )
        read_only_fields = ('id', 'email', 'role', 'created_at')

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is not correct.")
        return value
