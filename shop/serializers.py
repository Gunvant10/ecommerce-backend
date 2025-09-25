from rest_framework import serializers
from .models import UserProfile, Product, Cart, Order, OrderItem

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["phone", "address"]
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        
class CartSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    product = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'
        
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity"]
        
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    address = serializers.CharField(source="user.profile.address", read_only=True)
    phone = serializers.CharField(source="user.profile.phone", read_only=True)
    products = OrderItemSerializer(source="items", many=True, read_only=True) 
    
    class Meta:
        model = Order
        fields = ["id","user","products","total_price","status","shipping_address","address","phone","paid","created_at"]