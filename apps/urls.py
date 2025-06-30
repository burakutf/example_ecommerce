from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.routers import DefaultRouter
from .ecommerce import views

app_name = 'api'

schema_view = get_schema_view(
    openapi.Info(
        title='Snippets API',
        default_version='v1',
    ),
    public=True,
    permission_classes=(IsAuthenticated,),
)

router = DefaultRouter()

router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'attributes', views.AttributesViewSet, basename='attribute')
router.register(r'product-attributes', views.ProductAttributeViewSet, basename='product-attribute')

urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger'), name='schema-swagger-ui'),
] + router.urls 

