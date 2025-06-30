from django.db import models


class BaseModel(models.Model):
    """
    Başlangıç model, tüm modellerin ortak özelliklerini tanımlamak için kullanılır.
    Bu model, oluşturulma ve güncellenme zamanlarını otomatik olarak yönetir.
    """
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Kayıt işlemi sırasında, güncellenme zamanını otomatik olarak günceller.
        Eğer `update_fields` parametresi belirtilmişse, bu alana 'modified_time' eklenir.
        Bu, modelin güncellenme zamanının her kayıtta doğru şekilde tutulmasını sağlar.
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
    Özellikler, ürünlerin özelliklerini tanımlamak için kullanılır.
    Örneğin, malzeme gibi özellikler ürünlerin çeşitlerini belirlemek için kullanılır.
    Attributeler içerisinde dropdown, checkbox, selectable gibi seçenekler olabilir. fakat burada yapıyı
    basit tutmak adına sadece isim ve değer alanları ile tanımlıyoruz.
    Varyantlar, ürünlerin farklı varyasyonlarını tanımlamak için kullanılır.
    Örneğin, bir tişörtün farklı renk ve bedenleri gibi.
    Attributes ve Varyantlar arasındaki fark, Attributes'ın genel özellikleri tanımlarken,
    Varyantların belirli bir ürün varyasyonunu tanımlamasıdır.
    // Dipnot: sitemap.xml dosyasında bu modelin kullanımı, ürünlerin özelliklerini ve varyantlarını
    // daha iyi yönetmek ve SEO açısından optimize etmek için önemlidir.
    """
    name = models.CharField(max_length=128)
    is_visible = models.BooleanField(default=True)
    is_variant = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({'Variant' if self.is_variant else 'Attribute'})"


class ProductAttribute(BaseModel):
    """
    Ürün özellikleri, ürünlerin belirli özelliklerini tanımlamak için kullanılır.
    Bu model, ürünlerin özelliklerini ve varyantlarını ilişkilendirmek için kullanılır.
    Örneğin, bir tişörtün rengi veya bedeni gibi özellikler burada tanımlanır.
    """
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_attributes')
    attribute = models.ForeignKey(Attributes, on_delete=models.CASCADE, related_name='product_attributes')
    value = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"


class Category(BaseModel):
    """
    Kategori, ürünlerin gruplandırılması için kullanılır.
    Her kategori, bir isim ve isteğe bağlı olarak bir açıklama içerebilir.
    Kategoriler, ürünlerin daha düzenli ve erişilebilir olmasını sağlar.
    """
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class Product(BaseModel):
    """
    Base code aynı veya benzer ürünlerin gruplandırılması için kullanılır.
    SKU (Stock Keeping Unit) benzersiz bir ürün tanımlayıcısıdır.
    SKU, ürünün stok takibi ve yönetimi için kullanılır.
    SKU'da oluşan varyantlar aynı ürün gurubuna ait alt farklı ürün olarak tanımlanır,
    örneğin, bir tişörtün farklı renk ve bedenleri gibi.
    (Varyantlar, özelliklerin is_variant alanı True olarak işaretlenmiş olanlarıdır.)
    Buradaki `base_code` alanı, ürünlerin benzer özelliklere sahip gruplarını tanımlamak için kullanılır.
    Bu mimarinin genel amacı, Varyantlı ürünlerin yönetimini ve stok takibini kolaylaştırmaktır.
    """
    base_code = models.CharField(max_length=64)
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    attributes = models.ManyToManyField(Attributes, through='ProductAttribute', related_name='products')

    def __str__(self):
        return self.name
    