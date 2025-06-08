from django.contrib import admin
from .models import ImageModel, Category, Product, Cart, UserProfile, ContactUs, Review, Order, OrderItem, OrderHistory
# Registering models to admin panel
admin.site.register([ImageModel, Category, Product, Cart, UserProfile, ContactUs, Review, Order, OrderItem, OrderHistory])