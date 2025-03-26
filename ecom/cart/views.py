from django.shortcuts import render,redirect,get_object_or_404
from .models import Cart,Cartitems
from django.contrib.auth.models import User
from product.models import Product,ProductVariant
from django.contrib import messages
from userprofile.models import Address
from django.contrib.auth.decorators import login_required
from userprofile.forms import AddressForm
from coupons.models import Coupon

def cart(request):
    if not request.user.is_authenticated:
        return redirect('loginpage')
    try:
        cart = Cart.objects.get(user=request.user,is_active=True)
        cart_items = Cartitems.objects.filter(cart=cart,product__is_active=True,product__category_id__is_active=True)
        total_price = sum(item.total_price() for item in cart_items)

        
    except Cart.DoesNotExist:
        cart_items = []
        total_price = 0

    context={
        'cart_items':cart_items,
        'total_price':total_price,
    }

    return render(request,'cart.html',context)

def add_items_cart(request,product_id,size=None):
    if not request.user.is_authenticated:
        return redirect('loginpage')

    products = get_object_or_404(Product, id=product_id)
    user = request.user
    size_variant = products.variant.filter(size=size).first()

    quantity = int(request.POST.get('quantity', 1))
    
    cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    
    
    cart_item,created = Cartitems.objects.get_or_create(
        cart = cart,
        product = products,
        size = size,
        defaults= {'quantity':quantity}

    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    else:
        cart_item.save()

    messages.success(request,"product added to cart successfully")
    return redirect('cart')


def delete_items_cart(request,item_id):
    cart_item = get_object_or_404(Cartitems,id=item_id,cart__user = request.user)
    cart_item.delete()

    messages.success(request,"item is removed successfully!")
    return redirect('cart')


def update_cart(request,item_id):
    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(Cartitems, id=item_id)

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete() 

        return redirect('cart') 

    return redirect('cart')


def check_out(request):
    if not request.user.is_authenticated:
        return redirect('loginpage')
    try:
        
        cart = Cart.objects.get(user=request.user, is_active=True)
        cart_items = Cartitems.objects.filter(cart=cart)

        if not cart_items:
            request.session.pop('coupon_code', None)
            request.session.pop('discount_amount', None)
            messages.info(request, "Your cart is empty. Please add products to proceed to checkout.")
            return redirect('cart')  

        addresses = Address.objects.filter(user=request.user)
        total_price = sum(item.total_price() for item in cart_items)
        available_coupons = Coupon.objects.all()


        coupon_code = request.session.get('coupon_code')
        discount_amount = request.session.get('discount_amount',0)
        final_price = total_price - discount_amount

        context = {
            'cart_items': cart_items,
            'addresses': addresses,
            'total_price': total_price,
            'coupon_code': coupon_code,
            'discount_amount': discount_amount,
            'final_price': final_price,
            'available_coupons':available_coupons
        }
        return render(request, 'checkout.html', context)

    except Cart.DoesNotExist:
        messages.info(request, "Your cart is empty. Please add products to proceed to checkout.")
        return redirect('cart')



def add_address_checkout(request):

    form = AddressForm()

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('checkout')
    
    return render(request,'add_address_checkout.html',{'form':form})
