from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from .models import Address
from .forms import AddressForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from order.models import Order
from transaction.models import Transaction
from django.core.paginator import Paginator

def userprofile(request):
    if not request.user.is_authenticated:
        return redirect('loginpage')

    user = request.user
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')

    if request.method =='POST':
        if 'password_form' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request,"current password is incorrect")
            return redirect('userprofile')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('userprofile')
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('change_password')
        
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request,request.user)
        messages.success(request,'password changed successfully')
        return redirect('userprofile')
        
    return render(request,'userprofile.html',{'user':user,'addresses':addresses,'orders':orders,'transactions': transactions})

def useraddresslist(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request,'userprofile.html',{'addresses':addresses})


def add_address(request):

    form = AddressForm()

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('useraddresslist')
    
    return render(request,'add_address.html',{'form':form})

def edit_address(request,address_id):
    address=get_object_or_404(Address,id=address_id,user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST,instance=address)
        if form.is_valid():
            form.save()
            return redirect('useraddresslist')

    else:
        form = AddressForm(instance=address)

    return render(request,'edit_address.html',{'form':form,'item':address})


def delete_address(request,address_id):
    if request.method == 'POST':
        address = get_object_or_404(Address,id=address_id,user=request.user)
        address.delete()
        return redirect('useraddresslist')
    