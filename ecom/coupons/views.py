from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Coupon
from .forms import CouponCreateForm
from cart.models import Cart


def create_coupon(request):
    if request.method == "POST":
        form = CouponCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon created successfully!")
            return redirect("create_coupon")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CouponCreateForm()

    coupons = Coupon.objects.all()

    return render(request, "admin/coupon_create.html", {"form": form, "item": coupons})

def delete_coupon(request,coupon_id):
    alpha = get_object_or_404(Coupon,id=coupon_id)
    alpha.delete()
    messages.success(request, "Coupon deleted successfully.")
    return redirect('create_coupon')


def apply_coupon(request):
    if request.method=='POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=coupon_code)

            if not coupon.is_valid():
                messages.error(request,'coupon is expired or invalid')
                return redirect('checkout')

            cart = get_object_or_404(Cart,user=request.user,is_active=True)
            total_price = sum(item.total_price() for item in cart.cart_items.all())

            if total_price < coupon.min_purchase_amount:
                messages.error(request, f"Minimum purchase should be ₹{coupon.min_purchase_amount} to apply this coupon.")
                return redirect('checkout')

            request.session['coupon_code'] = coupon.code
            request.session['discount_amount'] = float(total_price * (coupon.discount_value / 100))

            messages.success(request, f"Coupon '{request.session['coupon_code']}' applied! Discount: ₹{request.session['discount_amount']}")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")

    return redirect('checkout')

def remove_coupon(request):
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
        del request.session['discount_amount']
        messages.success(request,'your coupon removed successfully.!')
    return redirect('checkout')