from django.db.models.signals import pre_save

from django.dispatch import receiver

from .models import Product


@receiver(pre_save, sender=Product)
def update_product_status(sender, instance, **kwargs):
    """
    Product kaydedildiğinde stok miktarına göre ürünün aktif/pasif durumunu günceller.
    Eğer stok miktarı sıfırsa ürün pasif hale gelir, aksi halde aktif hale gelir.
    Eğer ürün fiyatı sıfır ise ValueError fırlatılır.
    """
    if instance.price <= 0:
        raise ValueError("Product price must be greater than zero.")
    
    if instance.quantity <= 0:
        instance.is_active = False