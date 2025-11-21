from rest_framework import filters
class UserRentalFilter(filters.BaseFilterBackend):
    
    def filter_queryset(self, request, queryset, view):
        # Allow staff/superuser to see all rentals
        if request.user.is_staff or request.user.is_superuser:
            return queryset
        # Allow authenticated users to see their own rentals
        if request.user.is_authenticated:
            return queryset.filter(user=request.user)
        # For anonymous users, return empty queryset
        return queryset.none()