from rest_framework import serializers

from .models import Product, Category, ProductAttribute, Attributes


class AttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attributes
        fields = '__all__'


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute = AttributesSerializer(read_only=True)

    class Meta:
        model = ProductAttribute
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    product_attributes = ProductAttributeSerializer(many=True, read_only=True)
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = '__all__'
    
    def validate(self, attrs):
        if attrs.get('price', 0) <= 0:
            raise serializers.ValidationError("Product price must be greater than zero.")
        return attrs