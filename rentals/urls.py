from rest_framework.routers import DefaultRouter
from .views import RentalViewSet

router = DefaultRouter()
router.register(r'', RentalViewSet, basename='rental') #register the GET /rentals/ and POST /rentals/ endpoints

# For the return endpoint (PUT /rentals/{id}/return/), we will add a custom action 
# or a separate View/URL path next.

urlpatterns = router.urls