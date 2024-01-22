from django.db import models
from django.contrib.auth import get_user_model
from category.models import Category


# Create your models here.

User = get_user_model()
 
class Product(models.Model):
    STATUS_CHOICES = (('in_stock', 'В наличии'), ('out_of_stock', 'Нету в наличии'))
    owner = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'products')
    title = models.CharField(max_length = 255)
    category = models.ForeignKey(Category, on_delete = models.CASCADE, related_name = 'products')
    description = models.TextField(blank = True, null = True)
    image = models.ImageField(upload_to='images')
    price = models.DecimalField(max_digits = 9, decimal_places = 2)
    stock = models.CharField(max_length = 50, choices = STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
