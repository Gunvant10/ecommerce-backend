from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Product, Cart, Order, OrderItem

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Product)
class ProductAdminModel(admin.ModelAdmin):
    list_display = ["id","name","description","price"]

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "product", "quantity"]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "paid", "created_at"]
    list_filter = ["paid", "created_at"]
    search_fields = ["user__username", "id"]
    

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "product", "quantity"]