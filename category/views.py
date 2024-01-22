from django.shortcuts import render
from .models import Category
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .serializers import CategorySerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import permissions

# My views here.
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            return (permissions.IsAdminUser(),)
        return (permissions.AllowAny(),)

class CategoryAPIView(APIView):

    def get(self, request, slug = None):
        if slug:
            category = get_object_or_404(Category, slug = slug)
            serializer = CategorySerializer(category)
        else:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many = True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CategorySerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)