from django.urls import path,include
from . import views

urlpatterns = [
    path('transaction/list/',views.transaction_list,name='transaction_list'),
    path("wallet/add-money-form/", views.wallet_add_money_view, name="wallet_add_money_form"),
    path("wallet/add-money/", views.create_razorpay_wallet_order, name="create_razorpay_wallet_order"),
    path("wallet/payment-success/", views.razorpay_wallet_payment_success, name="razorpay_wallet_payment_success"),

]