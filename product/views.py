from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsAuthor
from rest_framework import permissions
from rest_framework.decorators import action
from rating.serializers import RatingSerializer
from rest_framework.response import Response
import logging
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

logger = logging.getLogger(__name__)


# Create your views here.
@method_decorator(cache_page(60*10), name='dispatch')

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return (IsAuthor(),)
        return (permissions.IsAuthenticatedOrReadOnly(),)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        cache.clear()

    def perform_destroy(self, instance):
        instance.delete()
        cache.clear()

    

    @action(['GET', "POST", 'DELETE'], detail=True)
    def ratings(self, request, pk):
        product = self.get_object()
        user = request.user

        if request.method == 'GET':
            rating = product.ratings.all()
            serializer = RatingSerializer(instance=rating, many=True)
            logger.info(f'Get request for ratings of product {pk} by user {user}')
            return Response(serializer.data, status=200)
        
        elif request.method == 'POST':
            if product.ratings.filter(owner = user).exists():
                return Response('Вы уже поставили оценку этому товару!', status=400)
            serializer = RatingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(owner=user, product = product)
            logger.info(f'Post request for ratings of product {pk} by user {user}')
            return Response(serializer.data, status=201)
        
        else:
            if not product.ratings.filter(owner = user).exists():   
                return Response('Вы не можете удалить оценку так как вы её не оставляли', status=400)
            rating = product.ratings.get(owner = user)
            rating.delete()
            logger.critical(f'Delete request for ratings of product {pk} by user {user}')
            return Response('Вы успешно удалили оценку!', status=204)
        
        