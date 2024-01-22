from django.db import models
from django.contrib.auth import get_user_model
from product.models import Product
from django.db.models.signals import post_save
from django.dispatch import receiver
from .send_email import sender_order_notification
from shopbooks.tasks import sender_order_notification_task

# Create your models here.


User = get_user_model()

class OrderStatus(models.TextChoices):
    in_process = 'in_process'
    completed = 'completed'

class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name = 'items', on_delete = models.CASCADE)
    product = models.ForeignKey(Product, related_name = 'items', on_delete = models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'{self.product.title}'
    
class Order(models.Model):
    user = models.ForeignKey(User, related_name = 'orders', on_delete = models.CASCADE)
    product = models.ManyToManyField(Product, through=OrderItem)
    address = models.CharField(max_length = 150)
    number = models.CharField(max_length = 150)
    status = models.CharField(max_length = 20, choices = OrderStatus, default = OrderStatus.in_process)
    total_sum = models.DecimalField(max_digits = 9, decimal_places = 2, blank = True)
    created_at = models.DateTimeField(auto_now_add = True)
    update_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f'{self.id} --> {self.user}'
    
@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, *args, **kwargs):
    if created:
        # sender_order_notification(instance.user.email, instance.id)
        sender_order_notification_task.delay(instance.user.email, instance.id)