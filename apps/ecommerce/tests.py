from django.test import TestCase
from decimal import Decimal 
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Product, Category, Attributes, ProductAttribute


class ProductSignalTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            description="This is a test category."
        )
        self.product = Product.objects.create(
            name="Test Product",
            base_code="TP001",
            sku="TEST123",
            price=Decimal("10.00"),
            quantity=5,
            is_active=True,
            category=self.category
        )

    def test_product_becomes_inactive_when_quantity_is_zero(self):
        """
        Tests that the product's is_active status becomes False when quantity is set to 0.
        """
        self.product.quantity = 0
        self.product.save()
        self.assertFalse(self.product.is_active)

        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)

    def test_product_remains_active_when_quantity_is_greater_than_zero(self):
        """
        Tests that the product's is_active status remains True when quantity is > 0.
        """
        self.product.quantity = 10
        self.product.save()
        self.assertTrue(self.product.is_active)
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_active)

    def test_value_error_raised_for_zero_price(self):
        """
        Tests that a ValueError is raised when the product price is 0.
        """
        self.product.price = Decimal("0.00")
        with self.assertRaises(ValueError) as cm:
            self.product.save()
        self.assertIn("Product price must be greater than zero.", str(cm.exception))

    def test_value_error_raised_for_negative_price(self):
        """
        Tests that a ValueError is raised when the product price is negative.
        """
        self.product.price = Decimal("-5.00")
        with self.assertRaises(ValueError) as cm:
            self.product.save()
        self.assertIn("Product price must be greater than zero.", str(cm.exception))

    def test_new_product_with_zero_quantity_is_inactive(self):
        """
        Tests that a newly created product with zero quantity is set to inactive by the signal.
        """
        new_product = Product(name="Zero Stock Item", price=Decimal("20.00"), quantity=0, category=self.category, base_code="ZSI001", sku="ZERO123")
        new_product.save()
        self.assertFalse(new_product.is_active)
        new_product.refresh_from_db()
        self.assertFalse(new_product.is_active)

    def test_new_product_with_positive_quantity_is_active(self):
        """
        Tests that a newly created product with positive quantity is active by default (signal doesn't change it).
        """
        new_product = Product(name="In Stock Item", price=Decimal("30.00"), quantity=10, category=self.category, base_code="ISI001", sku="INSTOCK123")
        new_product.save()
        self.assertTrue(new_product.is_active)
        new_product.refresh_from_db()
        self.assertTrue(new_product.is_active)

    def test_signal_does_not_interfere_with_valid_update(self):
        """
        Ensures that other valid updates to the product don't get blocked by the signal.
        """
        old_name = self.product.name
        self.product.name = "Updated Product Name"
        self.product.price = Decimal("15.00")
        self.product.quantity = 5
        self.product.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product Name")
        self.assertEqual(self.product.price, Decimal("15.00"))
        self.assertEqual(self.product.quantity, 5)
        self.assertTrue(self.product.is_active)

class ProductAPITest(APITestCase):

    def setUp(self):
        # Create a category
        self.category = Category.objects.create(name="Electronics", description="Electronic devices")

        # Create attributes
        self.color_attribute = Attributes.objects.create(name="Color", is_variant=True)
        self.size_attribute = Attributes.objects.create(name="Size", is_variant=True)
        self.material_attribute = Attributes.objects.create(name="Material", is_variant=False)

        # Create base product (main product for a base_code)
        self.product_tv_base = Product.objects.create(
            base_code="TV001",
            sku="TV001-MAIN",
            name="Smart TV 55 inch",
            price=1200.00,
            quantity=10,
            category=self.category,
            is_active=True
        )
        # Create ProductAttribute instances for the base product
        self.tv_base_color_attr = ProductAttribute.objects.create(
            product=self.product_tv_base,
            attribute=self.color_attribute,
            value="Black"
        )
        self.tv_base_size_attr = ProductAttribute.objects.create(
            product=self.product_tv_base,
            attribute=self.size_attribute,
            value="55-inch"
        )

        # Create a variant of the base product (same base_code, different SKU/attributes)
        self.product_tv_variant_silver = Product.objects.create(
            base_code="TV001",
            sku="TV001-SILVER",
            name="Smart TV 55 inch (Silver)",
            price=1250.00,
            quantity=5,
            category=self.category,
            is_active=True
        )
        # Create ProductAttribute instances for the silver variant
        self.tv_silver_color_attr = ProductAttribute.objects.create(
            product=self.product_tv_variant_silver,
            attribute=self.color_attribute,
            value="Silver"
        )
        self.tv_silver_size_attr = ProductAttribute.objects.create(
            product=self.product_tv_variant_silver,
            attribute=self.size_attribute,
            value="55-inch"
        )

        # Another variant for the same base code, but inactive
        self.product_tv_variant_red_inactive = Product.objects.create(
            base_code="TV001",
            sku="TV001-RED",
            name="Smart TV 55 inch (Red)",
            price=1100.00,
            quantity=2,
            category=self.category,
            is_active=False  # This variant is inactive
        )
        # Create ProductAttribute instances for the inactive red variant
        ProductAttribute.objects.create(
            product=self.product_tv_variant_red_inactive,
            attribute=self.color_attribute,
            value="Red"
        )
        ProductAttribute.objects.create(
            product=self.product_tv_variant_red_inactive,
            attribute=self.size_attribute,
            value="55-inch"
        )

        # Create a completely different product
        self.product_phone = Product.objects.create(
            base_code="PHONE001",
            sku="PHONE001-MAIN",
            name="Smartphone X",
            price=800.00,
            quantity=20,
            category=self.category,
            is_active=True
        )
        # Create ProductAttribute instances for the phone
        self.phone_color_attr = ProductAttribute.objects.create(
            product=self.product_phone,
            attribute=self.color_attribute,
            value="Blue"
        )

        # Updated URL names based on your router basename
        self.list_url = reverse('api:product-list') 

    def test_list_products_with_variants(self):
        """
        Test that the product list endpoint correctly groups products by base_code
        and includes their variants, filtering out inactive ones.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Expecting two base_codes: 'TV001' and 'PHONE001'
        self.assertEqual(len(data), 2)

        # Find the TV001 group
        tv_group = next(item for item in data if item['base_code'] == 'TV001')
        self.assertIsNotNone(tv_group)
        self.assertEqual(len(tv_group['variants']), 2) # Expecting 2 active variants (Black, Silver)

        # Check if the inactive variant is NOT present
        for variant in tv_group['variants']:
            self.assertNotEqual(variant['sku'], "TV001-RED")
            self.assertTrue(variant['is_active']) # All listed variants should be active

        # Check details of one of the TV variants
        black_tv_variant = next(
            (v for v in tv_group['variants'] if v['sku'] == "TV001-MAIN"),
            None
        )
        self.assertIsNotNone(black_tv_variant)
        self.assertEqual(black_tv_variant['name'], "Smart TV 55 inch")
        self.assertEqual(black_tv_variant['price'], '1200.00') # Price will be string from serializer

        silver_tv_variant = next(
            (v for v in tv_group['variants'] if v['sku'] == "TV001-SILVER"),
            None
        )
        self.assertIsNotNone(silver_tv_variant)
        self.assertEqual(silver_tv_variant['name'], "Smart TV 55 inch (Silver)")

        # Find the PHONE001 group
        phone_group = next(item for item in data if item['base_code'] == 'PHONE001')
        self.assertIsNotNone(phone_group)
        self.assertEqual(len(phone_group['variants']), 1)
        self.assertEqual(phone_group['variants'][0]['sku'], "PHONE001-MAIN")

    def test_create_product_with_attributes(self):
        """
        Test creating a new product with its associated product attributes.
        This test now correctly creates ProductAttribute instances first,
        then passes their IDs to product_attributes_ids.
        """
        # First, create the ProductAttribute instances you want to associate
        # with the new product. This simulates a client sending existing attribute IDs.
        temp_product_attr_color = ProductAttribute.objects.create(
            attribute=self.color_attribute, value="Blue", product=None # product is temporary None
        )
        temp_product_attr_material = ProductAttribute.objects.create(
            attribute=self.material_attribute, value="Aluminum", product=None # product is temporary None
        )

        new_product_data = {
            "base_code": "LAPTOP001",
            "sku": "LAPTOP001-BLUE",
            "name": "Gaming Laptop (Blue)",
            "price": "1500.00",
            "quantity": 8,
            "is_active": True,
            "category_id": self.category.id, # Using 'category' field name as per the error, not 'category_id'
            "product_attributes": [ # Pass PKs of ProductAttribute instances
                {"attribute_id": temp_product_attr_color.attribute.id, "value": temp_product_attr_color.value},
                {"attribute_id": temp_product_attr_material.attribute.id, "value": temp_product_attr_material.value}
            ]
        }
        response = self.client.post(self.list_url, new_product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.text) # Print error if not 201

        # Verify the product and its attributes were created and linked
        created_product = Product.objects.get(sku="LAPTOP001-BLUE")
        self.assertEqual(created_product.name, "Gaming Laptop (Blue)")
        self.assertEqual(created_product.product_attributes.count(), 2)

        # Check if the ProductAttribute instances are now correctly linked to the new product
        linked_color_attr = created_product.product_attributes.get(attribute=self.color_attribute)
        self.assertEqual(linked_color_attr.value, "Blue")

        linked_material_attr = created_product.product_attributes.get(attribute=self.material_attribute)
        self.assertEqual(linked_material_attr.value, "Aluminum")

    def test_update_product_and_attributes(self):
        """
        Test updating an existing product and its associated product attributes.
        Correctly handles required fields for ProductWriteSerializer by passing ProductAttribute PKs.
        """
        # Updated URL name
        detail_url = reverse('api:product-detail', kwargs={'pk': self.product_tv_base.id})

        """ 
        To update, we modify the existing ProductAttribute instances, or create new ones
        For this test, let's assume we want to keep the color but change its value
        and add a new material attribute.
        We also need to get the PKs of the ProductAttribute instances we want to *keep*
        or *link*.
        
        Scenario 1: Update an existing attribute (e.g., color) and add a new one (material)
        Note: If your serializer's M2M update logic implies replacing all ProductAttributes
        when product_attributes_ids is provided, then you'd need to include the PKs of ALL
        desired ProductAttribute instances for the product.

        Let's say we want to change the color of self.product_tv_base and add a material attribute.
        We need to create a new ProductAttribute for the material, and potentially modify the existing color one.
        
        Modify existing color attribute (e.g., its value) or create a new one for a new value
        For simplicity in the test, we'll assume the serializer handles updating based on attribute_id+product_id
        or that we pass the PK of the exact ProductAttribute instance we want to associate.

        Since the error indicates PKs are expected for `product_attributes_ids`,
        we prepare the PKs of `ProductAttribute` objects that should be associated
        with `self.product_tv_base` AFTER the update.

        Create a new ProductAttribute for the material specifically for this update scenario"""
        new_material_product_attr = ProductAttribute.objects.create(
            attribute=self.material_attribute, value="Plastic", product=self.product_tv_base
        )
        
        """        
        We need the PKs of the *desired* ProductAttribute instances after the update.
        This will include the original size attribute and the newly created material attribute,
        assuming the color attribute is *removed* or *replaced* by omission.
        If the serializer only adds, this logic will need adjustment.
        
        Based on your previous error ("Invalid pk"), your ProductWriteSerializer's
        `product_attributes_ids` field likely expects a list of PKs of existing ProductAttribute instances.
        This means you must have already created these ProductAttribute objects
        with the correct `product` and `attribute` values.
        
        For an update, we assume the serializer *replaces* the many-to-many relationship.
        So we supply the PKs of the ProductAttribute objects we want associated.
        
        Let's create new ProductAttribute instances for the updated values
        and use their IDs for the update payload.
        This simulates a client creating or selecting specific ProductAttribute objects
        and linking them.

        Create a new ProductAttribute for the updated color (e.g., Charcoal)"""
        updated_color_product_attr = ProductAttribute.objects.create(
            product=self.product_tv_base, 
            attribute=self.color_attribute, 
            value="Charcoal"
        )

        # We will link the updated_color_product_attr and new_material_product_attr
        # to self.product_tv_base. This implies removing the original black color and 55-inch size attributes.
        
        updated_data = {
            "base_code": self.product_tv_base.base_code,
            "sku": self.product_tv_base.sku,
            "name": "Smart TV 55 inch (Updated)",
            "price": "1300.00",
            "quantity": 15,
            "is_active": True,
            "category_id": self.category.id, # Using 'category' field name
            "product_attributes": [ # Pass PKs of ProductAttribute instances
                {
                    "attribute_id": updated_color_product_attr.attribute.id,
                    "value": updated_color_product_attr.value,
                },
                {
                    "attribute_id": new_material_product_attr.attribute.id,
                    "value": new_material_product_attr.value,
                }
            ]
        }
        
        response = self.client.put(detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.text) # Print error if not 200

        self.product_tv_base.refresh_from_db()
        self.assertEqual(self.product_tv_base.name, "Smart TV 55 inch (Updated)")
        self.assertEqual(self.product_tv_base.price, 1300.00)
        
        # After update, it should have 2 attributes based on our payload
        self.assertEqual(self.product_tv_base.product_attributes.count(), 2) 

        # Verify the new attributes are linked
        linked_color_attr = self.product_tv_base.product_attributes.get(attribute__id=updated_color_product_attr.attribute.id)
        self.assertEqual(linked_color_attr.value, "Charcoal")

        linked_material_attr = self.product_tv_base.product_attributes.get(attribute__id=new_material_product_attr.attribute.id)
        self.assertEqual(linked_material_attr.value, "Plastic")

        # Verify the old attributes are gone (the original black color and 55-inch size)
        with self.assertRaises(ProductAttribute.DoesNotExist):
            ProductAttribute.objects.get(id=self.tv_base_color_attr.id) # Original black TV color
        with self.assertRaises(ProductAttribute.DoesNotExist):
            ProductAttribute.objects.get(id=self.tv_base_size_attr.id) # Original 55-inch size

    def test_delete_product(self):
        """
        Test deleting a product.
        """
        # Updated URL name
        detail_url = reverse('api:product-detail', kwargs={'pk': self.product_phone.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.filter(id=self.product_phone.id).count(), 0)
        self.assertEqual(ProductAttribute.objects.filter(product=self.product_phone).count(), 0) # Associated attributes should also be deleted

    def test_filter_products_by_category(self):
        """
        Test filtering products by category.
        """
        # Create another category and product
        category_clothes = Category.objects.create(name="Clothes")
        Product.objects.create(
            base_code="SHIRT001", sku="SHIRT001-BLUE", name="T-Shirt",
            price=25.00, quantity=50, category=category_clothes
        )

        response = self.client.get(self.list_url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # All products with base_code TV001 and PHONE001 belong to self.category
        # We expect 2 base_codes from the Electronics category
        self.assertEqual(len(data), 2)
        self.assertTrue(any(item['base_code'] == 'TV001' for item in data))
        self.assertTrue(any(item['base_code'] == 'PHONE001' for item in data))
        self.assertFalse(any(item['base_code'] == 'SHIRT001' for item in data))

