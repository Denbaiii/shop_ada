from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = '__all__'

# class CategorySerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only = True)
#     slug = serializers.SlugField(read_only = True)
#     name = serializers.CharField(max_length = 50, required = True)

#     def create(self, validated_data):
#         return Category.objects.create(**validated_data)
    
#     def update(self, instance, validated_data):
#         instance.name = validated_data.get('name', instance.name)
#         instance.save()
#         return instance