from django.test import TestCase
from .models import Category, Product
from decimal import Decimal 


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