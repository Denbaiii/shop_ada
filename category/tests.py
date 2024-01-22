from django.test import TestCase
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from .models import Category
from .views import CategoryViewSet


# Create your tests here.

User = get_user_model()

class CategotyTest(APITestCase):
    def setUp(self, *args, **kwargs):
        self.factory = APIRequestFactory()
        self.setup_category()
        self.user = self.setup_user()

    def setup_category(self):
        # Category.objects.create(name='category-1')
        # Category.objects.create(name='category-2')
        # Category.objects.create(name='category-3')

        list_categories = []
        for i in range(1, 101):
            list_categories.append(Category(name = f'category{i}', slug = f'slug{i}'))
        Category.objects.bulk_create(list_categories)

    def setup_user(self):
        return User.objects.create_superuser('test@gmail.com', '1')
    
    def test_get_category(self):
        request = self.factory.get('api/categories')
        view = CategoryViewSet.as_view({'get':'list'})
        response = view(request)

        assert response.status_code == 200
        assert Category.objects.count() == 100
        assert Category.objects.first().name == 'category1'

    def test_post_category(self):
        data = {
            'name':'test_category'
        }
        request = self.factory.post('api/categories', data)
        force_authenticate(request, user = self.user)
        view = CategoryViewSet.as_view({'post':'create'})
        response = view(request)

        assert response.status_code == 201
        assert Category.objects.filter(name = 'test_category').exists()

    def test_update_category(self):
        category = Category.objects.first()
        data = {'name':'updated_category'}
        request = self.factory.patch(f'api/categories{category.slug}/', data)
        force_authenticate(request, user = self.user)
        view = CategoryViewSet.as_view({'patch':'partial_update'})
        response = view(request, slug = category.slug)

        category.refresh_from_db()
        assert response.status_code == 200
        assert category.name == 'updated_category'

    def test_delete_category(self):
        category = Category.objects.first()
        request = self.factory.delete(f'api/categories/{category.slug}/')
        force_authenticate(request, user = self.user)
        view = CategoryViewSet.as_view({'delete':'destroy'})
        response = view(request, slug = category.slug)

        assert response.status_code == 204
        assert not Category.objects.filter(slug = category.slug).exists()