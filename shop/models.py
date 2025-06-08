import os

from django.db import models


def upload_path(instance, filename):
    return os.path.join("uploads", filename)


class ImageModel(models.Model):
    image = models.ImageField(upload_to=upload_path, null=False, blank=True)
    created_date = models.DateTimeField(null=False, blank=True, auto_now_add=True)


from django.db import models


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    Catname = models.CharField(max_length=100)


class Product(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    Pname = models.CharField(max_length=100)
    P_image = models.ImageField(upload_to='shop/uploads/', null=True, blank=True)
    P_desc = models.TextField()
    P_brand = models.CharField(max_length=100)
    P_price = models.DecimalField(max_digits=10, decimal_places=2)
    P_catid = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    cust_id = models.EmailField(max_length=100)
    product = models.ForeignKey(Product, related_name="cart_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class UserProfile(models.Model):
    Name = models.CharField(max_length=100)
    Password = models.CharField(max_length=255)
    Email = models.EmailField(unique=True)
    Address = models.TextField()
    City = models.CharField(max_length=100)
    State = models.CharField(max_length=100)
    Phone = models.CharField(max_length=15, unique=True)
    Pincode = models.CharField(max_length=6)


class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    pincode = models.CharField(max_length=6)
    feedback_desc = models.TextField()


class Review(models.Model):
    cust_id = models.EmailField(max_length=100)
    username = models.CharField(max_length=100)
    description = models.TextField()
    stars = models.PositiveIntegerField()
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)


class Order(models.Model):
    cust_id = models.EmailField(max_length=100)
    C_name = models.CharField(max_length=100)
    ord_date = models.DateField()
    C_phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    address = models.TextField()
    pincode = models.CharField(max_length=6)
    total = models.DecimalField(max_digits=10, decimal_places=2)


class OrderItem(models.Model):
    ord_id = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()


class OrderHistory(models.Model):
    ord_id = models.ForeignKey(Order, related_name="order_history", on_delete=models.CASCADE)
    cust_id = models.EmailField(max_length=100)
    C_name = models.CharField(max_length=100)
    ord_date = models.DateField()
    C_phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    pincode = models.CharField(max_length=6)

