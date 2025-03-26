from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from product.models import Product, ProductVariant
from .models import Wishlist, WishlistItem

def wishlist_view(request):

    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.wish.all()

    return render(request,'wishlist.html',{'wishlist_items':wishlist_items})

def add_items_wishlist(request,product_id):
    product = get_object_or_404(Product,id=product_id)
    size = request.GET.get('size')

    if size:
        product_variant = get_object_or_404(ProductVariant,size=size,product=product)

    else:
        product_variant = ProductVariant.objects.filter(product=product).first()
        if not product_variant:
            messages.error(request,'no sizes available for this product !')
            return redirect('shop')
    
    wishlist,created = Wishlist.objects.get_or_create(user=request.user)

    wishlist_item,created = WishlistItem.objects.get_or_create(wishlist=wishlist,product=product,product_variant=product_variant)

    if created:
        messages.success(request, f"{product.name} ({product_variant.size}) added to wishlist!")
    else:
        messages.info(request, "This product is already in your wishlist!")

    return redirect('wishlist_view')


def remove_items_wishlist(request,item_id):
    wishlist_items = get_object_or_404(WishlistItem,id =item_id,wishlist__user=request.user)
    wishlist_items.delete()
    messages.success(request,'your item removed successfully !')

    return redirect('wishlist_view')
