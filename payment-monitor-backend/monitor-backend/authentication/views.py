from sre_parse import expand_template
from rest_framework import generics
from .serializers import RegisterSerializer
from api.models import User


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
