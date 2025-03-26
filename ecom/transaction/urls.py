from django.urls import path,include
from . import views

urlpatterns = [
    path('transaction/list/',views.transaction_list,name='transaction_list')

]