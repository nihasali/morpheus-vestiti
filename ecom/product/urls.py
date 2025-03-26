from django.urls import path
from . import views

urlpatterns =[
    path('product/create/',views.create_product,name ='create_product'),
    path('product/list/',views.product_list,name = 'product_list'),
    path('product/edit/<int:id>/',views.edit_product,name = 'edit_product'),
    path('product/unlist/<int:id>/',views.product_unlist,name = 'product_unlist'),
    path('product/variant/list/<int:product_id>/',views.variant_list,name='variant_list'),
    path('product/variant/create/<int:product_id>/',views.add_variant,name='add_variant'),
    path('product/variant/edit/<int:id>/<int:product_id>/',views.edit_variant,name='edit_variant'),
    path('user/product/list',views.shop_list,name='shop_list'),
    path('user/product/details/<int:id>/',views.product_details,name='product_details'),

]