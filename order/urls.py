from django.urls import path
from .views import OrderAPIView, OrderConfirmView

urlpatterns = [
    path('', OrderAPIView.as_view()),
    path('confirm/<int:pk>/', OrderConfirmView.as_view()),

]