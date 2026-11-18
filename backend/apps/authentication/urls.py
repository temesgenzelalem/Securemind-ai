from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'authentication'

urlpatterns = [
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
