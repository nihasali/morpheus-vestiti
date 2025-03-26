import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from product.models import Product,ProductVariant
from userprofile.models import Address
from cart.models import Cart,Cartitems
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from reportlab.pdfgen import canvas
from io import BytesIO
from django.db.models import Q
from django.core.paginator import Paginator
from userprofile.models import Wallet
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from coupons.models import Coupon
from transaction.models import Transaction

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def place_order(request):
    if request.method == "POST":
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method', '').strip().lower()
        print(f"Received Payment Method----------: '{payment_method}'")

        if not address_id or not payment_method:
            messages.error(request, "Please select an address and payment method.")
            return redirect('checkout')

        address = get_object_or_404(Address, id=address_id, user=request.user)
        cart = get_object_or_404(Cart, user=request.user, is_active=True)
        cart_items = cart.cart_items.all()

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('checkout')

        
        total_price = sum(item.total_price() for item in cart_items)
        real_price = total_price

        coupon_code = request.session.get('coupon_code')
        discount_amount = request.session.get('discount_amount', 0)
        final_price = total_price - discount_amount

        coupon = None
        if coupon_code:
            coupon = Coupon.objects.filter(code=coupon_code).first()


        if payment_method == 'razorpay':
            amount = int(final_price * 100)  


            razorpay_order = razorpay_client.order.create({
                'amount': amount,
                'currency': 'INR',
                'payment_capture': '1'
            })


            print("Generated Razorpay Order ID:", razorpay_order.get('id'))
            if not razorpay_order.get('id'):
                messages.error(request, "Failed to generate Razorpay Order ID.")
                return redirect('checkout')


            
            order = Order.objects.create(
                user=request.user,
                address=address,
                payment_method=payment_method,
                total_price=final_price,
                real_price=real_price,
                coupon=coupon,
                discount_amount=discount_amount,
                status='failed',
                razorpay_order_id=razorpay_order['id'],
                created_at=timezone.now()
            )

            return redirect('razorpay_payment', order_id=order.id)

        if payment_method == 'cod':
            if final_price >= 1000:
                messages.error(request,'COD only available for purchase below 1000')
                return redirect('checkout')
            
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    address=address,
                    payment_method=payment_method,
                    total_price=final_price,
                    real_price=real_price,
                    coupon=coupon,
                    discount_amount=discount_amount,
                    status='pending',  
                    created_at=timezone.now()
                )

                for item in cart_items:
                    variant = get_object_or_404(ProductVariant, product=item.product, size=item.size)

                    if variant.stock < item.quantity:
                        messages.error(request, f"Insufficient stock for {item.product.name} (Size: {item.size}).")
                        transaction.set_rollback(True)
                        return redirect('checkout')

                    
                    variant.stock -= item.quantity
                    variant.save()

                    
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        size_variant=variant,
                        quantity=item.quantity,
                        price=item.product.price - (item.product.price * (item.product.offer / 100))
                    )

                
                cart.cart_items.all().delete()
                cart.is_active = False
                cart.save()

                request.session.pop('coupon_code', None)
                request.session.pop('discount_amount', None)


            messages.success(request, "Your order has been placed successfully!")
            return redirect('order_success', order_id=order.id)
        
        if payment_method == 'wallet':
            wallet=Wallet.objects.filter(user=request.user).first()

            if not wallet or Decimal(wallet.balance) < Decimal(final_price):
                messages.error(request,'Insufficient Wallwt balance. Select another payment method!.')
                return redirect('checkout')
            
            with transaction.atomic():
                wallet.balance = Decimal(wallet.balance) - Decimal(final_price)
                wallet.save()


                order=Order.objects.create(
                    user=request.user,
                    address=address,
                    payment_method=payment_method,
                    total_price=final_price,
                    real_price=real_price,
                    coupon=coupon,
                    discount_amount=discount_amount,
                    status='paid',
                    created_at=timezone.now()
                )

                for item in cart_items:
                    variant = get_object_or_404(ProductVariant, product=item.product,size=item.size)

                    if variant.stock < item.quantity:
                        messages.error(request, f"Insufficient stock for {item.product.name} (Size: {item.size}).")
                        transaction.set_rollback(True)
                        return redirect('checkout')

                    variant.stock -= item.quantity
                    variant.save()

                    OrderItem.objects.create(
                        order = order,
                        product = item.product,
                        size_variant = variant,
                        quantity = item.quantity,
                        price = item.product.price,
                        status = 'paid'

                    )

                Transaction.objects.create(
                    user = request.user,
                    order = order,
                    payment_method = payment_method,
                    amount = final_price,
                    status = 'paid'

                )

                cart.cart_items.all().delete()
                cart.is_active = False
                cart.save()

                request.session.pop('coupon_code', None)
                request.session.pop('discount_amount', None)

            messages.success(request, "Your order has been placed successfully using Wallet!")
            return redirect('order_success', order_id=order.id)

    return redirect('checkout')


def razorpay_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    context = {
        'order': order,
        'razorpay_key': settings.RAZORPAY_KEY_ID,  
        'amount': int(order.total_price * 100),
        'razorpay_order_id': order.razorpay_order_id,  
    }

    return render(request, 'razorpay_payment.html', context)

@csrf_exempt
def razorpay_callback(request, order_id):
    if request.method == "POST":
        data = request.POST
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        order = get_object_or_404(Order, id=order_id, razorpay_order_id=razorpay_order_id)

        if not order:
            return JsonResponse({"error": "Order not found"}, status=400)

        
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            with transaction.atomic():
                
                cart = Cart.objects.filter(user=order.user, is_active=True).first()
                if cart:
                    cart_items = list(cart.cart_items.all()) 
                else:
                    cart_items = []
                
                order.status = "paid"
                order.save()

                for item in cart_items:
                    variant = get_object_or_404(ProductVariant, product=item.product, size=item.size)

                    if variant.stock < item.quantity:
                        messages.error(request, f"Insufficient stock for {item.product.name} (Size: {item.size}).")
                        transaction.set_rollback(True)
                        return JsonResponse({"error": "Stock issue"}, status=400)

                    
                    variant.stock -= item.quantity
                    variant.save()

                    
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        size_variant=variant,
                        quantity=item.quantity,
                        price=item.product.price,
                        status = 'paid'
                    )

                if cart:
                    cart.cart_items.all().delete()
                    cart.is_active = False
                    cart.save()

                request.session.pop('coupon_code', None)
                request.session.pop('discount_amount', None)

            return redirect('order_success', order_id=order.id)

        except razorpay.errors.SignatureVerificationError:
            order.status = "failed"
            order.save()
            return JsonResponse({"error": "Signature verification failed"}, status=400)


def retry_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='failed')

    amount = int(order.total_price * 100)
    razorpay_order = razorpay_client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1'
    })

    order.razorpay_order_id = razorpay_order['id']
    order.save()

    return redirect('razorpay_payment', order_id=order.id)


def payment_failed(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.status = 'failed'
    order.save()
    messages.error(request, "Payment failed or was cancelled. You can retry.")
    return render(request,'order_failed.html', {'order':order})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})



def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'userprofile.html', {'orders': orders})


def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    cart = None

    cart = Cart.objects.filter(user=request.user, is_active=True).first()
    cart_items = Cartitems.objects.filter(cart=cart) or None

    for item in order_items:
        item.total_price = item.price * item.quantity
    return render(request, 'order_details.html', {'order': order,'order_items':order_items,'cart_items':cart_items})


def cancel_order(request,order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order,id=order_id,user=request.user)
        reason = request.POST.get('reason','').strip()

        if order.status == 'pending' and reason:
            order.status = 'canceled'
            order.reason = reason
            order.save()

            for item in order.items.all():
                size_variant = item.size_variant
                size_variant.stock += item.quantity  
                size_variant.save()

                item.status = 'canceled'
                item.reason = reason
                item.save()

            messages.success(request,"your item cancelled successfully !")
        
        elif order.status == 'paid' and reason:
            order.status = 'canceled'
            order.reason = reason
            order.save()

            total_refund= Decimal(order.total_price)

            for item in order.items.all():
                size_variant = item.size_variant
                size_variant.stock += item.quantity
                size_variant.save()

                item.status = 'canceled'
                item.reason = reason
                item.save()

            wallet,created = Wallet.objects.get_or_create(user=order.user)
            wallet.balance = Decimal(wallet.balance) + total_refund
            wallet.save()

            Transaction.objects.create(
                user=order.user,
                order=order,
                payment_method=order.payment_method,
                amount=total_refund,
                status='canceled'
            )

            messages.success(request,'return accepted and amount credited to wallet!')


        else:
            messages.error(request,'your order cannot be cancelled or reason missing !')
    return redirect('order_details', order_id=order_id)

def cancel_order_item(request,order_id,item_id):
    if request.method == 'POST':
        order = get_object_or_404(Order,id=order_id,user=request.user)
        order_item = get_object_or_404(OrderItem,id=item_id,order=order)

        active_items_count = order.items.exclude(status='canceled').count()
        if active_items_count <= 1:
            messages.error(request, 'Only one item left in the order. Please cancel the whole order instead.')
            return redirect('order_details', order_id=order_id)

        if order_item.status == 'pending':
            order_item.status = 'canceled'
            order.total_price = order.total_price - order_item.price * order_item.quantity
            order_item.save()
            order.save()

            
            size_variant = order_item.size_variant
            size_variant.stock += order_item.quantity
            size_variant.save()

            all_items_canceled = not order.items.exclude(status='canceled').exists()
            if all_items_canceled:
                order.status = 'canceled'
                order.save()
                messages.info(request, "All items are canceled, so the order has been marked as 'canceled'.")
            
            messages.success(request,'your ordered product is canceled successfully!')

        elif order_item.status == 'paid':
            order_item.status = 'canceled'
            order.total_price = order.total_price - order_item.price * order_item.quantity
            order_item.save()
            order.save()

            total_refund = Decimal(order_item.price) * order_item.quantity

            size_variant = order_item.size_variant
            size_variant.stock += order_item.quantity
            size_variant.save()

            wallet,created = Wallet.objects.get_or_create(user=order.user)
            wallet.balance = Decimal(wallet.balance) + total_refund
            wallet.save()

            Transaction.objects.create(
                user=order.user,
                order=order,
                payment_method=order.payment_method,
                amount=total_refund,
                status='canceled'
            )

            all_items_canceled = not order.items.exclude(status='canceled').exists()
            if all_items_canceled:
                order.status = 'canceled'
                order.save()
                messages.info(request, "All items are canceled, so the order has been marked as 'canceled'.")

            messages.success(request,'your ordered product is cancelled refund will be credited to your wallet!')

        else :
            messages.error(request,'this item cannot be cancelled! or reason is missing')

    return redirect('order_details',order_id=order_id)

def return_order_item(request,order_id,item_id):
    if request.method == 'POST':
        order = get_object_or_404(Order,id=order_id,user=request.user)
        order_item = get_object_or_404(OrderItem,id=item_id,order=order)

        active_items_count = not order.items.exclude(status='returned').count()
        if active_items_count <= 1:
            messages.error(request, 'Only one item left in the order. Please return the whole order instead.')
            return redirect('order_details', order_id=order_id)

        if order_item.status == 'delivered':
            order_item.status = 'returned'
            order.total_price = order.total_price - order_item.price * order_item.quantity
            order_item.save()
            order.save()

            total_refund = Decimal(order_item.price) * order_item.quantity

            size_variant = order_item.size_variant
            size_variant.stock += order_item.quantity
            size_variant.save()

            wallet,created = Wallet.objects.get_or_create(user=order.user)
            wallet.balance = Decimal(wallet.balance) + total_refund
            wallet.save()

            Transaction.objects.create(
                user=order.user,
                order=order,
                payment_method=order.payment_method,
                amount=total_refund,
                status='returned'
            )

            messages.success(request,'return accepted and amount credited to wallet!')
        else:
            messages.error(request,'this item cannot be returned!')
    
    return redirect('order_details',order_id=order_id)


def return_order(request,order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order,id=order_id,user=request.user)
        reason = request.POST.get('reason','').strip()


        if order.status == 'delivered' and reason:
            order.request = 'requested'
            order.status = 'return_req'
            order.reason = reason
            order.save()

        for item in order.items.all():
            item.status = 'return_req'
            item.reason = reason
            item.save()

        messages.success(request,'your return order requested successfully !')

    else:
        messages.error(request,'your order cannot be returned!')

    return redirect('order_details',order_id = order_id) 


def admin_return_accept(request,order_id):
    order = get_object_or_404(Order,id=order_id)
    action = request.POST.get('action')

    if order.request == 'requested':
        if action == 'accepted':
            order.request = 'accepted'
            order.status = 'returned'
            order.save()
        
            total_refund= Decimal(order.total_price)
            for item in order.items.all():
                item.status = 'returned'
                item.save()

                size_variant=item.size_variant
                size_variant.stock += item.quantity
                size_variant.save()

            wallet, created = Wallet.objects.get_or_create(user=order.user)
            wallet.balance = Decimal(wallet.balance) + total_refund
            wallet.save()

            Transaction.objects.create(
                user=order.user,
                order=order,
                payment_method=order.payment_method,
                amount=total_refund,
                status='returned'
            )

            messages.success(request,'return accepted and amount credited to wallet!')

        elif action == 'rejected':
            order.request = ''
            order.save()
            messages.error(request,'return is rejected !')
    else:
        messages.error(request, 'Invalid action!')


    return redirect('admin_order_details',order_id=order_id) 




def admin_order_list(request):
    if not request.user.is_superuser:
        return redirect('admin_login')

    
    search = request.GET.get('search','')
    status = request.GET.get('status','')
    if search:
        orders=Order.objects.filter(
            Q(id__icontains=search) | Q(user__username__icontains=search) | Q(status__icontains=search)
        )
    else:
        orders = Order.objects.all().order_by('-created_at')
    
    if status and status!= 'all':
        orders = Order.objects.filter(status__icontains = status)
        

    paginator = Paginator(orders,8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'admin/admin_orderlist.html',{'page_obj':page_obj,'search':search,'status':status})

def admin_order_details(request,order_id):
    if not request.user.is_superuser:
        return redirect('admin_login')

    order = get_object_or_404(Order,id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    prev = request.GET.get('prev', 'orderlist')

    for item in order_items:
        item.total_price = item.price * item.quantity


    if request.method == 'POST':
        if order.status == 'completed':
            messages.warning(request,'Order is already completed. Status cannot be changed!.')
            return redirect('admin_order_details', order_id=order.id)

        new_status = request.POST.get('status')
        if new_status in dict(Order.ORDER_STATUS_CHOICES):
            order.status = new_status
            order.save()
            for item in order_items:
                if item.status not in ['canceled','returned']:
                    item.status = new_status
                    item.save()
                
            messages.success(request,'your order status changed successfully!')
    
    return render(request,'admin/admin_order_detail.html',{'order':order,'order_items':order_items,'prev':prev})



@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Morpheus Vestiti - Invoice")
    p.setFont("Helvetica", 12)
    p.drawString(50, 780, f"Order ID: {order.id}")
    p.drawString(50, 760, f"Order Date: {order.created_at.strftime('%Y-%m-%d')}")
    p.drawString(50, 740, f"Customer: {request.user.username}")

    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 710, "Shipping Address:")
    p.setFont("Helvetica", 12)
    p.drawString(50, 690, f"{order.address.address}")
    p.drawString(50, 675, f"{order.address.city}, {order.address.state}")
    p.drawString(50, 660, f"{order.address.zipcode}")

    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 630, "Product")
    p.drawString(300, 630, "Quantity")
    p.drawString(400, 630, "Price")
    p.drawString(500, 630, "Total")

    
    y = 610
    p.setFont("Helvetica", 12)
    for item in order_items:
        item_total = item.price * item.quantity
        p.drawString(50, y, item.product.name)
        p.drawString(300, y, str(item.quantity))
        p.drawString(400, y, f"${item.price:.2f}")
        p.drawString(500, y, f"${item_total:.2f}")
        y -= 20

    
    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(400, y, "Subtotal:")
    p.drawString(500, y, f"${order.real_price:.2f}")

    if order.discount_amount:
        y -= 20
        p.drawString(400, y, "Discount:")
        p.drawString(500, y, f"-${order.discount:.2f}")

    y -= 20
    p.drawString(400, y, "Grand Total:")
    p.drawString(500, y, f"${order.total_price:.2f}")

    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response