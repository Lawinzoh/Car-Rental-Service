"""
Custom middleware for handling shared admin and public paths.
"""
from django.db import connection
from django_tenants.middleware import TenantMiddleware as BaseTenantMiddleware
from django_tenants.utils import get_public_schema_name
from django.http import HttpResponseNotFound


class CustomTenantMiddleware(BaseTenantMiddleware):
    """
    Custom TenantMiddleware that allows admin and public paths to work
    in the public schema without requiring a tenant domain.
    """
    
    PUBLIC_PATHS = ['/admin/', '/api/token/', '/api/token/refresh/', '/api/schema/', '/users/']
    
    def process_request(self, request):
        # Check if this is a request to a public path
        for public_path in self.PUBLIC_PATHS:
            if request.path.startswith(public_path):
                # Set to public schema and skip tenant resolution
                connection.set_schema_to_public()
                return None
        
        # Otherwise, use the default tenant middleware logic
        return super().process_request(request)
