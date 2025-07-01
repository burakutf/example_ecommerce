from django.db import models


class BaseModel(models.Model):
    """
    BaseModel is used to define common attributes for all models.
    It automatically manages the creation and modification timestamps.
    """
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        This save method ensures that the modified_time is updated automatically
        whenever the model instance is saved. If `update_fields` is provided,
        it appends 'modified_time' to the list, ensuring that this field is always
        """
        update_fields = kwargs.get("update_fields", None)
        if update_fields is not None:
            if isinstance(update_fields, set):
                update_fields = list(update_fields)
            update_fields.append("modified_time")
            kwargs["update_fields"] = update_fields
        super(BaseModel, self).save(*args, **kwargs)


class Attributes(BaseModel):
    """
    Attributes are used to define the characteristics of products.
    For example, material attributes can be used to define product variations.
    Attributes can include options like dropdowns, checkboxes, and selectables,
    but for simplicity, we define them with just a name and value field.
    Variants are used to define different variations of products,
    such as different colors and sizes of a t-shirt.
    The difference between Attributes and Variants is that Attributes define general characteristics,
    while Variants define a specific product variation.
    Attributes and Variants are essential for managing product characteristics and variations,
    especially in e-commerce systems where products can have multiple attributes and variations.
    """
    name = models.CharField(max_length=128, unique=True, db_index=True)
    is_visible = models.BooleanField(default=True)
    is_variant = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({'Variant' if self.is_variant else 'Attribute'})"


class ProductAttribute(BaseModel):
    """
    ProductAttribute is used to link products with their attributes.
    It allows for the association of a product with various attributes,
    such as color, size, or material.
    Each product can have multiple attributes, and each attribute can be linked to multiple products.
    This model is essential for managing product variations and attributes in an e-commerce system.
    """
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_attributes', null=True)
    attribute = models.ForeignKey(Attributes, on_delete=models.CASCADE, related_name='product_attributes')
    value = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"


class Category(BaseModel):
    """
    Category is used to group products.
    Each category can have a name and an optional description.
    Categories help in organizing products for better accessibility.
    """
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class Product(BaseModel):
    """
    The base code is used to group similar or identical products together.
    SKU (Stock Keeping Unit) is a unique product identifier.
    SKU is used for stock tracking and management.
    Variants in SKU are defined as different products within the same product group,
    for example, different colors and sizes of a t-shirt.
    Variants are those attributes marked with is_variant as True.
    The `base_code` field here is used to define groups of products with similar attributes.
    The overall purpose of this architecture is to facilitate the management and stock tracking of products with variants.
    """
    base_code = models.CharField(max_length=64, db_index=True)
    sku = models.CharField(max_length=64, unique=True)
    image = models.ImageField(upload_to='media/products/', null=True)
    name = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    attributes = models.ManyToManyField(Attributes, through='ProductAttribute', related_name='products')

    def __str__(self):
        return self.name + f" ({self.sku})"
    