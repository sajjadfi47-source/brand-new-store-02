from django.urls import path
from . import views
urlpatterns=[
 path("",views.home,name="home"),path("shop/",views.shop,name="shop"),
 path("product/<slug:slug>/",views.product_detail,name="product_detail"),
 path("cart/",views.cart,name="cart"),path("cart/add/<int:pk>/",views.add_cart,name="add_cart"),
 path("cart/update/",views.cart_update,name="cart_update"),path("checkout/",views.checkout,name="checkout"),
 path("product/<int:pk>/whatsapp/",views.whatsapp,name="whatsapp"),
]
