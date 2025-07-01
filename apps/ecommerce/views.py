from rest_framework import viewsets

from django.http import JsonResponse

# Serializer'ları import ediyoruz
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    AttributesSerializer,
    ProductAttributeSerializer,
)
from .models import Product, Category, Attributes, ProductAttribute
from django.db.models import Min # Aggregation için


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        'category',
    ).prefetch_related(
        'product_attributes__attribute',
    )
    serializer_class = ProductSerializer
    search_fields = ['name', 'sku', 'base_code']
    filterset_fields = ['category', 'is_active', 'base_code']
    ordering_fields = ['name']

    def list(self, request, *args, **kwargs):
        initial_queryset = self.filter_queryset(self.get_queryset())

        unique_base_codes_ids = initial_queryset.values('base_code').annotate(
            min_id=Min('id')
        ).values_list('min_id', flat=True)

        main_products = initial_queryset.filter(id__in=list(unique_base_codes_ids)).order_by('id')

        results = []
        for main_product in main_products:
            validated_data = ProductSerializer(main_product).data
            data = [validated_data]
            if not validated_data.get('is_active'):
                data = []

            product_data = {
                'base_code': main_product.base_code,
                'variants': data
            }
            variants_queryset = self.get_queryset().filter(base_code=main_product.base_code).exclude(id=main_product.id)
            for variant in variants_queryset:
                variant_data = ProductSerializer(variant).data
                if not variant_data.get('is_active'):
                    continue
                product_data['variants'].append(variant_data)

            results.append(product_data)
        return JsonResponse(results, safe=False)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name'] 
    ordering_fields = ['name', 'created_time']

class ProductAttributeViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribute.objects.select_related('product', 'attribute').all()
    filterset_fields = ['product', 'attribute']
    serializer_class = ProductAttributeSerializer
    

class AttributesViewSet(viewsets.ModelViewSet):
    queryset = Attributes.objects.all()
    serializer_class = AttributesSerializer
    search_fields = ['name']
    filterset_fields = ['is_variant', 'is_visible']
    ordering_fields = ['name', 'is_variant']