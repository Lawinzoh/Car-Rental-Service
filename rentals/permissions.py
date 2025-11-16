from rest_framework import permissions

class IsRentalUserOrAdmin(permissions.BasePermission):
    """Allow users to only see rentals they created, or admins see all"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.user == request.user