from django.shortcuts import render
from .models import Transaction
from django.contrib.auth.decorators import login_required

def transaction_list(request):
    transactions = Transaction.objects.select_related('user','order').order_by('-created_at')

    return render(request,'admin/transaction.html',{'transactions':transactions})
