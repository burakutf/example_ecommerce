from rest_framework import viewsets
from rest_framework.viewsets import mixins

from .models import Product, Category, ProductAttribute, Attributes
from .serializers import ProductSerializer, CategorySerializer, ProductAttributeSerializer, AttributesSerializer


class ProductViewSet(viewsets.ModelViewSet):
    # Sorgu setini optimize etmek için select_related ve prefetch_related kullanıyoruz
    queryset = Product.objects.select_related(
        'category',
    ).prefetch_related(
        'product_attributes__attribute',
    )
    serializer_class = ProductSerializer
    search_fields = ['name']
    filterset_fields = ['category', 'is_active']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    

class ProductAttributeViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer


class AttributesViewSet(viewsets.ModelViewSet):
    queryset = Attributes.objects.all()
    serializer_class = AttributesSerializer