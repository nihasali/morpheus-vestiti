from django.urls import path
from . import views

urlpatterns = [
    path('categories/list/',views.category_list,name='category_list'),
    path('categories/create/',views.create_category,name ='create_category'),
    path('categories/edit/<int:id>/',views.edit_category,name ='edit_category'),
    path('categories/unlist/<int:id>/',views.unlist_category,name ='unlist_category'),

]