import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions
from .models import Product, Cart, Order, OrderItem
from .serializers import ProductSerializer, CartSerializer, OrderSerializer
from django.utils.decorators import method_decorator

stripe.api_key = settings.STRIPE_SECRET_KEY


# ---------- Product ----------
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# ---------- Cart ----------
class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        carts = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data

        # If user sends a list of products
        if isinstance(data, list):
            carts = []
            for item in data:
                product_id = item.get("product_id")
                quantity = int(item.get("quantity", 1))

                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return Response({"error": f"Product {product_id} not found"}, status=404)

                cart = Cart.objects.create(user=request.user, product=product, quantity=quantity)
                carts.append(cart)

            return Response(CartSerializer(carts, many=True).data, status=201)

        # If user sends a single product
        else:
            product_id = data.get("product_id")
            quantity = int(data.get("quantity", 1))

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"error": "Product not found"}, status=404)

            cart = Cart.objects.create(user=request.user, product=product, quantity=quantity)
            return Response(CartSerializer(cart).data, status=201)

    def delete(self, request):
        cart_id = request.data.get("cart_id")
        try:
            cart = Cart.objects.get(id=cart_id, user=request.user)
            cart.delete()
            return Response({"message": "Item removed"})
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=404)
        

# ---------- Orders ----------
class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        shipping_address = request.data.get("shipping_address", "")
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        # Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # convert rupees to paisa
            currency="inr",
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never"
                }
        )

        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_price=total_amount,
            stripe_payment_intent=intent["id"],
            shipping_address=shipping_address if shipping_address else request.user.profile.address
        )

        # Create Order Items from cart
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        # Clear Cart
        cart_items.delete()

        return Response({
            "id": order.id,
            "user": request.user.username,
            "total_price": str(order.total_price),
            "status": order.status,
            "shipping_address": order.shipping_address
        })


class OrderHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)



# ---------- Pay order ----------
@method_decorator(csrf_exempt, name="dispatch")
class PayOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        payment_method_id = request.data.get("payment_method_id")

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        if order.paid:
            return Response({"message": "Order already paid"}, status=400)

        try:
            # Confirm the Stripe payment
            intent = stripe.PaymentIntent.confirm(
                order.stripe_payment_intent,
                payment_method=payment_method_id
            )

            if intent["status"] == "succeeded":
                order.paid = True
                order.status = "completed"
                order.save()
                return Response({"message": "Payment successful", "order_id": order.id, "status": order.status})

            else:
                return Response({"message": "Payment failed", "status": intent["status"]}, status=400)

        except stripe.error.CardError as e:
            return Response({"error": str(e)}, status=400)



# ---------- Stripe Webhook ----------
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = ""  # optional

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        order = Order.objects.filter(stripe_payment_intent=intent["id"]).first()
        if order:
            order.paid = True
            order.status = "paid"
            order.save()

    return HttpResponse(status=200)
