from rest_framework import serializers

from .models import Product, Category, ProductAttribute, Attributes


class AttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attributes
        fields = '__all__'


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute = AttributesSerializer(read_only=True)
    attribute_id = serializers.PrimaryKeyRelatedField(
        queryset=Attributes.objects.all(),
        source='attribute'  # Map to the `attribute` field in the model
    )

    class Meta:
        model = ProductAttribute
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    product_attributes = ProductAttributeSerializer(many=True)  # Nested serializer
    category = CategorySerializer(read_only=True)  # Read-only serializer
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category'  # Map to the `category` field in the model
    )

    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        product_attributes_data = validated_data.pop('product_attributes', [])

        product = Product.objects.create(**validated_data)
        # TODO: bulk create for performance
        for attribute_data in product_attributes_data:
            ProductAttribute.objects.create(product=product, **attribute_data)

        return product

    def update(self, instance, validated_data):
        product_attributes_data = validated_data.pop('product_attributes', [])
        instance = super().update(instance, validated_data)

        instance.product_attributes.all().delete()
        # TODO: bulk create for performance
        for attribute_data in product_attributes_data:
            ProductAttribute.objects.create(product=instance, **attribute_data)

        return instance
    