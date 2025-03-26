from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.userprofile,name='userprofile'),
    path('address/list/',views.useraddresslist,name='useraddresslist'),
    path('address/add/',views.add_address,name='add_address'),
    path('address/edit/<int:address_id>/',views.edit_address,name='edit_address'),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),



]