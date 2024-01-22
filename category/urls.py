from django.urls import path
from .views import CategoryViewSet, CategoryAPIView

urlpatterns = [
    # path('category/', CategoryViewSet.as_view({'get': 'list'})),
    # path('category/<int:pk>/', CategoryViewSet.as_view({'get': 'retrieve'})),
    # path('categories/', CategoryAPIView.as_view()),
    # path('categories/<slug:slug>/', CategoryAPIView.as_view()),
]