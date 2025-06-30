from django.contrib import admin

from apps.ecommerce.models import Product, Category, Attributes, ProductAttribute

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active', 'category')

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Attributes)
admin.site.register(ProductAttribute)
