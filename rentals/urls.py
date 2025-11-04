# rentals/urls.py

from rest_framework.routers import DefaultRouter
from .views import RentalViewSet, DamageReportViewSet, ReviewViewSet
from django.urls import path

# --- 1. Define View Functions (Method Mapping) ---
report_create_view = DamageReportViewSet.as_view({'post': 'create'})
review_create_view = ReviewViewSet.as_view({'post': 'create'})
rental_extend_view = RentalViewSet.as_view({'put': 'extend_rental'}) # <<< Define the extend action

urlpatterns = [
    # A. Damage Report Creation: POST /rentals/reports/
    path('reports/', report_create_view, name='damage-report-list'),
    
    # B. Review Creation: POST /rentals/reviews/
    path('reviews/', review_create_view, name='review-list'),

    # C. Rental Extension: PUT /rentals/{id}/extend/ 
    path('<int:pk>/extend/', rental_extend_view, name='rental-extend'),
]

# --- 3. Add Router Paths (Handles /rentals/, /rentals/{id}/, etc.) ---
router = DefaultRouter()
router.register(r'', RentalViewSet, basename='rental')

# Append the router's URLs to the list
urlpatterns += router.urls