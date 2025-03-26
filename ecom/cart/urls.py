from django.urls import path,include
from . import views

urlpatterns = [
    path('cart/',views.cart,name = 'cart'),
    path('cart/add/<int:product_id>/<str:size>/',views.add_items_cart,name = 'add_items_cart'),
    path('cart/delete/<int:item_id>/', views.delete_items_cart, name='delete_items_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/checkout/',views.check_out,name='checkout'),
    path('add/address/checkout/',views.add_address_checkout,name='add_address_checkout')

    
]