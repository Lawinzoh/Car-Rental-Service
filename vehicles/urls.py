from rest_framework.routers import DefaultRouter
from .views import VehicleListView

router = DefaultRouter()
# Register the VehicleViewSet to handle all CRUD actions under the base 'cars' path
router.register(r'', VehicleListView, basename='vehicle') # Register the vehicles app routes

urlpatterns = router.urls