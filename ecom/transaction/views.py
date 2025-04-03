from django.shortcuts import render,redirect
from .models import Transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import razorpay
from django.conf import settings
from django.http import JsonResponse
from userprofile.models import Wallet
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import json

def transaction_list(request):
    transactions_qs = Transaction.objects.select_related('user','order').order_by('-created_at')

    paginator = Paginator(transactions_qs, 6)  
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)

    return render(request,'admin/transaction.html',{'transactions':transactions})


def wallet_add_money_view(request):
    return render(request, "wallet_add_money.html",{
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })

def create_razorpay_wallet_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            amount = int(data.get("amount"))

            if amount < 1000:
                return JsonResponse({"error": "Minimum ₹10 required"}, status=400)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            order_data = {"amount": amount, "currency": "INR", "payment_capture": "1"}
            razorpay_order = client.order.create(data=order_data)

            return JsonResponse({"order_id": razorpay_order["id"], "amount": amount})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def razorpay_wallet_payment_success(request):
    try:
        data = json.loads(request.body)

        payment_id = data.get("payment_id")
        amount = data.get("amount")

        if not payment_id or not amount:
            return JsonResponse({"success": False, "error": "Invalid payment data"}, status=400)

        amount = Decimal(amount) / 100

        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += amount
        wallet.save()

        Transaction.objects.create(
            user = request.user,
            payment_method = 'Razorpay-credited',
            amount = amount,
            status = 'credited')

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)