from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework import generics

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