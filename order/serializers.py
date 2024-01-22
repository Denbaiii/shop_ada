from rest_framework import serializers
from .models import OrderItem, Order


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.ReadOnlyField(source='product.title')

    class Meta:
        model = OrderItem
        fields = ('product', 'product_title', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    user = serializers.ReadOnlyField(source='user.email')
    products = OrderItemSerializer(write_only=True, many=True)

    class Meta:
        model = Order
        exclude = ('product',)

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        request = self.context.get('request')
        user = request.user

        total_sum = 0
        order_items = []

        order = Order.objects.create(user=user, status='in_process', total_sum=total_sum, **validated_data)

        for product_data in products_data:
            product = product_data['product']
            quantity = product_data['quantity']
            total_sum += quantity * product.price

            order_item = OrderItem.objects.create(order=order, product=product, quantity=quantity)
            order_items.append(order_item)

        order.total_sum = total_sum
        order.save()

        order.items.set(order_items)
        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['products'] = OrderItemSerializer(instance.items.all(), many=True).data
        return representation
