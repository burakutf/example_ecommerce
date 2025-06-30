🚀 Django E-commerce API
Bu proje, Django ve Django REST Framework kullanarak geliştirilmiş, temel bir e-ticaret uygulamasının API katmanını sunar. Ürünler, kategoriler ve ürün özelliklerini yönetmek için sağlam bir yapı sağlar.

🌟 Özellikler
Ürün Yönetimi: Ürünleri oluşturma, okuma, güncelleme ve silme (CRUD) işlemleri.

Kategori Yönetimi: Ürünleri kategorize etmek için kategori yönetimi.

Ürün Özellikleri ve Varyantları: Ürünlere renk, boyut gibi özellikler ekleme ve varyantları yönetme yeteneği.

Otomatik Zaman Damgaları: BaseModel ile tüm modellerde created_time ve modified_time alanlarının otomatik yönetimi.

Ürün Durumu Otomatik Güncelleme: Stok miktarına göre ürünlerin aktif/pasif durumunu otomatik olarak güncelleyen signal yapısı.

API Kimlik Doğrulaması: Session ve Token tabanlı kimlik doğrulama.

API Dokümantasyonu: DRF-YASG ile Swagger UI üzerinden otomatik API dokümantasyonu.

Docker Desteği: Docker ve Docker Compose ile kolay kurulum ve dağıtım.

Çevre Değişkenleri: .env dosyası ile hassas bilgilerin ve yapılandırmaların güvenli yönetimi.

🛠️ Teknolojiler
Django: Web çatısı

Django REST Framework: RESTful API'ler oluşturmak için güçlü araçlar

PostgreSQL (veya SQLite): Veritabanı yönetimi

DRF-YASG: Otomatik API dokümantasyonu (Swagger/OpenAPI)

django-environ: Çevre değişkeni yönetimi

django-cors-headers: CORS yönetimi

Docker & Docker Compose: Konteynerleştirme

🚀 Kurulum ve Çalıştırma
Ön Gereksinimler
Docker ve Docker Compose yüklü olmalıdır.

1. Projeyi Klonlayın
Bash

git clone <proje-deposu-url>
cd example_ecommerce
2. Çevre Değişkenlerini Ayarlayın
Proje kök dizininde .env adında bir dosya oluşturun ve aşağıdaki içeriği ekleyin. Değerleri kendi ortamınıza göre düzenleyebilirsiniz.

Kod snippet'i

SECRET_KEY=your_super_secret_key_here
DEBUG=True

# PostgreSQL Ayarları (isteğe bağlı, SQLite için bu bölümü silin veya yorumlayın)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=ecommerce_password
DB_HOST=db
DB_PORT=5432
3. Docker Compose ile Başlatın
Bash

docker-compose up --build
Bu komut, Docker imajlarını oluşturacak, veritabanını (eğer PostgreSQL kullanılıyorsa) ve Django uygulamasını başlatacaktır.

4. Veritabanı Migrasyonları ve Süper Kullanıcı Oluşturma
Uygulama kapsayıcısı çalışmaya başladıktan sonra, veritabanı migrasyonlarını uygulamak ve bir süper kullanıcı oluşturmak için aşağıdaki komutları çalıştırın:

Bash

docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
Komut istemlerini takip ederek süper kullanıcınızı oluşturun.

5. API'ye Erişin
Uygulama varsayılan olarak http://localhost:8000 adresinde çalışacaktır.

API Ana Noktaları: http://localhost:8000/api/

Swagger UI Dokümantasyonu: http://localhost:8000/api/swagger/

Django Admin Paneli: http://localhost:8000/admin/ (Oluşturduğunuz süper kullanıcı bilgileriyle giriş yapabilirsiniz.)

📝 Modeller
Projedeki temel modeller ve işlevleri aşağıda açıklanmıştır:

BaseModel
Tüm diğer modeller için temel bir soyut modeldir. Otomatik olarak created_time (oluşturulma zamanı) ve modified_time (güncellenme zamanı) alanlarını yönetir. save metodu, update_fields parametresi kullanıldığında bile modified_time'ın doğru şekilde güncellenmesini sağlar.

Attributes
Ürünlerin genel özelliklerini (örneğin, "Renk", "Beden", "Malzeme") veya varyant özelliklerini tanımlar.

name: Özelliğin adı.

is_visible: Özelliğin dışarıdan görünür olup olmadığını belirtir.

is_variant: Bu özelliğin bir ürün varyantı için kullanılıp kullanılmadığını belirtir.

ProductAttribute
Bir ürün ile bir özellik (Attributes) arasındaki ilişkiyi kurar ve bu özelliğin değerini (value) tutar. Örneğin, "Tişört" ürününün "Renk" özelliği için "Kırmızı" değeri gibi.

Category
Ürünlerin organize edildiği kategorileri tanımlar. Her kategori bir name ve isteğe bağlı bir description'a sahiptir.

Product
E-ticaret sistemindeki ana ürünü temsil eder.

base_code: Aynı veya benzer ürünlerin (varyantlar dahil) gruplandırılması için kullanılır.

sku: Ürünün stok takibi için kullanılan benzersiz bir Stock Keeping Unit (SKU) kodudur.

name: Ürünün adı.

price: Ürünün fiyatı.

quantity: Ürünün mevcut stok miktarı.

is_active: Ürünün stok durumuna göre (quantity <= 0 ise False, aksi halde True) otomatik olarak güncellenen aktiflik durumu.

category: Ürünün ait olduğu kategori.

attributes: Ürüne atanan özellikler (ProductAttribute modeli üzerinden).

🚦 Sinyaller
update_product_status
Product modeli her kaydedildiğinde devreye giren bir pre_save sinyalidir.

Eğer ürünün price değeri 0 veya daha düşükse bir ValueError fırlatır.

Eğer ürünün quantity değeri 0 veya daha düşükse, is_active alanı False olarak ayarlanır.

Eğer ürünün quantity değeri 0dan büyükse, is_active alanı True olarak ayarlanır.

🌐 API Uç Noktaları (Routes)
Aşağıdaki API uç noktaları http://localhost:8000/api/ altında mevcuttur:

/products/: Ürünler için CRUD işlemleri.

/categories/: Kategoriler için CRUD işlemleri.

/attributes/: Özellikler için CRUD işlemleri.

/product-attributes/: Ürün özelliklerini ilişkilendirmek ve yönetmek için CRUD işlemleri.

/swagger/: Swagger UI üzerinden API dokümantasyonu.

/swagger<format>/: API dokümantasyonunun JSON/YAML formatında alınması.

⚙️ Yapılandırma (settings.py)
Veritabanı: .env dosyasındaki DB_ENGINE, DB_NAME, vb. değişkenler aracılığıyla PostgreSQL veya SQLite arasında seçim yapabilirsiniz.

DRF Ayarları: Sayfalandırma, renderer sınıfları, filtreleme backend'leri, izin sınıfları ve kimlik doğrulama sınıfları yapılandırılmıştır.

CORS: CORS_ALLOW_ALL_ORIGINS = True ve CORS_ALLOW_CREDENTIALS = True olarak ayarlanmıştır, bu da herhangi bir kaynaktan gelen CORS isteklerine izin verir. Geliştirme ortamı için uygundur, üretimde kısıtlanmalıdır.

Debug Modu: DEBUG True olduğunda, DRF izin sınıfları AllowAny olarak ayarlanır, bu da geliştirme sırasında kimlik doğrulamayı devre dışı bırakır.

🧪 Testler
Proje, sinyal ve model davranışlarını doğrulamak için kapsamlı testlere sahiptir. Testleri çalıştırmak için:

Bash

docker-compose exec web python manage.py test ecommerce
