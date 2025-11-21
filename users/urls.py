# users/urls.py

from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ClientViewSet, DomainViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')  # Register the users app routes
router.register(r'clients', ClientViewSet, basename='client')  # Register clients (tenants) management
router.register(r'domains', DomainViewSet, basename='domain')  # Register domains management

urlpatterns = router.urls
