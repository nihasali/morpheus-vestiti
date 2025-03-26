from django.urls import path
from . import views


urlpatterns =[
    path('wishlist/add/<int:product_id>/', views.add_items_wishlist, name='add_items_wishlist'),
    path('wishlist/list/',views.wishlist_view,name = 'wishlist_view'),
    path('wishlist/remove/<int:item_id>/',views.remove_items_wishlist,name='remove_items_wishlist')

]