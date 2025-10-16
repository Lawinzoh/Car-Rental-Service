import django_filters
from .models import Vehicle

class VehicleFilter(django_filters.FilterSet):
    #filter by a range of years
    year_min = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    year_max = django_filters.NumberFilter(field_name='year', lookup_expr='lte')

    #filter by case-insensitive partial match on 'make'
    make = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Vehicle
        fields = ['make', 'model', 'year', 'availability_status']