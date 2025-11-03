from rest_framework.routers import DefaultRouter
from .views import RentalViewSet, DamageReportViewSet
from django.urls import path

# Damage Report Creation Endpoint: POST /reports/
report_create_view = DamageReportViewSet.as_view({'post': 'create'})
urlpatterns = [
    path('reports/', report_create_view, name='damage-report-list'),
]
router = DefaultRouter()
router.register(r'reports', DamageReportViewSet, basename='damage-report')
#rental route
router.register(r'', RentalViewSet, basename='rental')

urlpatterns += router.urls