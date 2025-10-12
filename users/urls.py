# users/urls.py

from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)  # Register the users app routes

urlpatterns = router.urls