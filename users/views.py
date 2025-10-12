from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all() # Fetch all users
    serializer_class = UserSerializer #for handling serialization and deserialization
     # Authentication will be added in Week 4 [cite: 50]
    # Permissions will be added in Week 4 [cite: 50]
