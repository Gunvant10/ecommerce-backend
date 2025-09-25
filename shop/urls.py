from django.urls import path
from .views import (
    ProductListView, CartView, CreateOrderView, OrderHistoryView, PayOrderView, stripe_webhook
)

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("cart/", CartView.as_view(), name="cart"),
    path("create-order/", CreateOrderView.as_view(), name="create-order"),
    path("orders/", OrderHistoryView.as_view(), name="order-history"),
    path("pay-order/", PayOrderView.as_view(), name="order-payment"),
    path("stripe-webhook/", stripe_webhook, name="stripe-webhook"),
]
