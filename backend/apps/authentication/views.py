from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.models import User
from apps.authentication.serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)
from apps.organizations.models import Organization, Membership
from apps.audit.models import AuditLog

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            email = request.data.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                AuditLog.objects.create(
                    organization=user.current_organization,
                    actor=user,
                    action='user_login',
                    target_type='User',
                    target_id=str(user.id),
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details={'method': 'jwt_password'}
                )
        return response

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens immediately upon registration
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['role'] = user.role
        refresh['full_name'] = user.full_name
        if user.current_organization:
            refresh['org_id'] = str(user.current_organization.id)
            refresh['org_name'] = user.current_organization.name

        AuditLog.objects.create(
            organization=user.current_organization,
            actor=user,
            action='user_registered',
            target_type='User',
            target_id=str(user.id),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        return Response({
            'user': UserProfileSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class ChangePasswordView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)

class SwitchOrganizationView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        org_id = request.data.get('organization_id')
        if not org_id:
            return Response({'error': 'organization_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure user is an active member of this organization
        membership = Membership.objects.filter(
            user=request.user,
            organization_id=org_id,
            is_active=True
        ).select_related('organization').first()

        if not membership and not request.user.is_superuser:
            return Response({'error': 'You do not have access to this organization'}, status=status.HTTP_403_FORBIDDEN)

        org = membership.organization if membership else Organization.objects.filter(id=org_id).first()
        request.user.current_organization = org
        request.user.save(update_fields=['current_organization'])

        return Response({
            'message': f'Switched active organization to {org.name}',
            'current_organization': {
                'id': str(org.id),
                'name': org.name,
                'slug': org.slug
            }
        }, status=status.HTTP_200_OK)
