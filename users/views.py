from rest_framework import viewsets, status
from .models import User, Client, Domain
from .serializers import UserSerializer, ClientSerializer, DomainSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all() # Fetch all users
    serializer_class = UserSerializer #for handling serialization and deserialization
     
    def get_permissions(self):
        # Allow POST (create/registration) requests for ALL users (unauthenticated)
        if self.action == 'create': 
            permission_classes = [AllowAny]
        # Only Admins can view the full list of users
        elif self.action == 'list':
            permission_classes = [IsAdminUser] 
        # All other actions (Retrieve, Update, Delete) require authentication
        else:
            permission_classes = [IsAuthenticated] 
            
        return [permission() for permission in permission_classes]


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenants/clients.
    Only accessible to admin/owner users.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        # Admin can see all clients
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Client.objects.all()
        return Client.objects.none()
    
    def perform_create(self, serializer):
        """Create a new client/tenant"""
        client = serializer.save()
        return client


class DomainViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing domains for tenants.
    Only accessible to admin/owner users.
    """
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        # Filter by client_id if provided
        client_id = self.request.query_params.get('client_id')
        if client_id:
            return Domain.objects.filter(tenant_id=client_id)
        return Domain.objects.all()