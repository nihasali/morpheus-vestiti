from django.urls import path
from . import views

urlpatterns =[
    path('coupon/create/',views.create_coupon,name='create_coupon'),
    path('coupon/delete/<int:coupon_id>/',views.delete_coupon,name='delete_coupon'),
    path("coupon/apply/", views.apply_coupon, name="apply_coupon"),
    path('coupo/remove/',views.remove_coupon,name='remove_coupon'),


]