from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow users to only see/edit vehicles they own, or admins see all"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.owner == request.user