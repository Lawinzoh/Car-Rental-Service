import django_filters
from .models import Vehicle
from rest_framework import filters

class VehicleFilter(django_filters.FilterSet):
    #filter by a range of years
    year_min = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    year_max = django_filters.NumberFilter(field_name='year', lookup_expr='lte')

    #filter by case-insensitive partial match on 'make'
    make = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Vehicle
        fields = ['make', 'model', 'year', 'availability_status']

class OwnerFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        # Allow staff/superuser to see all vehicles
        if request.user.is_staff or request.user.is_superuser:
            return queryset
        # Allow authenticated users to see their own vehicles + public vehicles (owner=None)
        if request.user.is_authenticated:
            return queryset.filter(owner__in=[request.user, None])
        # For anonymous users, only show vehicles with no owner
        return queryset.filter(owner__isnull=True)