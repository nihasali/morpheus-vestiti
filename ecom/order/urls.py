from django.urls import path
from . import views


urlpatterns =[
    path('placeorder/',views.place_order,name='placeorder'),
    path('order_success/<int:order_id>/',views.order_success,name='order_success'),
    path('orders/list/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_details, name='order_details'),
    path('admin/order/list/',views.admin_order_list,name='admin_order_list'),
    path('admin/order/details/<int:order_id>/',views.admin_order_details,name='admin_order_details'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order/<int:order_id>/invoice/', views.download_invoice, name='download_invoice'),
    path('order/return/<int:order_id>/',views.return_order,name = 'return_order'),
    path('order/return/accept/<int:order_id>/',views.admin_return_accept,name='admin_return_accept'),
    path('order/razorpay-payment/<int:order_id>/', views.razorpay_payment, name='razorpay_payment'),
    path('order/razorpay-callback/<int:order_id>/', views.razorpay_callback, name='razorpay_callback'),
    path('order/cancel/item/<int:order_id>/<int:item_id>/',views.cancel_order_item,name = 'cancel_order_item'),
    path('order/return/item/<int:order_id>/<int:item_id>/',views.return_order_item,name = 'return_order_item'),
    path('order/retry/<int:order_id>/',views.retry_payment,name='retry_payment'),
     path('order/failure/<int:order_id>/',views.payment_failed,name='payment_failed'),

]