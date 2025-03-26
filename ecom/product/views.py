from django.shortcuts import render,redirect,get_object_or_404
from .models import Product,ProductVariant
from admin_category.models import Categories
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from decimal import Decimal


@login_required(login_url='admin_login')
def create_product(request):
    if not request.user.is_superuser:
        return redirect('admin_login')


    item = Product.objects.order_by('id').all()
    error = None
    categories = Categories.objects.filter(is_active=True)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category_id')
        offer = request.POST.get('offer')
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')

        if not name:
            messages.error(request, 'Product name is required.')
            return redirect('create_product')

        if Product.objects.filter(name__iexact=name).exists():
            messages.error(request, 'Product with this name already exists.')
            return redirect('create_product')

        if not description:
            messages.error(request, 'Description is required.')
            return redirect('create_product')
        

        try:
            price = Decimal(price)
            if price <= 0:
                messages.error(request, "Price must be greater than zero.")
                return redirect('create_product')
        except InvalidOperation:
            messages.error(request, "Invalid price. Please enter a valid number.")
            return redirect('create_product')

        try:
            offer = Decimal(offer) if offer else Decimal(0)
            if offer < 0:
                messages.error(request, "Offer cannot be negative.")
                return redirect('create_product')
            if offer > 80:
                messages.error(request, "Offer cannot exceed 80%.")
                return redirect('create_product')
        except InvalidOperation:
            messages.error(request, "Invalid offer. Please enter a valid number.")
            return redirect('create_product')

        if not category_id:
            messages.error(request, 'Category is required.')
            return redirect('create_product')

        category = get_object_or_404(Categories, id=category_id)


        if not any([image1, image2, image3]):
            messages.error(request, "At least one product image is required.")
            return redirect('create_product')

        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        for image in [image1, image2, image3]:
            if image:
                
                if image.content_type == 'application/pdf':
                    messages.error(request, "PDF files are not allowed. Please upload images only!")
                    return redirect('create_product')
                
                if image.content_type not in allowed_types:
                    messages.error(request, "Only JPEG, PNG, and GIF image files are allowed!")
                    return redirect('create_product')

        alpha = Product.objects.create(name = name,description=description,original_price=price,price=int(price),category_id=category,offer=offer,image1=image1,image2=image2,image3=image3)
        alpha.save()

        return redirect('product_list')

    return render(request,'admin/create_product.html',{'item':item,'categories':categories})


@login_required(login_url='admin_login')
def product_list(request):
    if not request.user.is_superuser:
        return redirect('admin_login')

    item = Product.objects.order_by('-id').all()

    paginator = Paginator(item, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/product_list.html', {'page_obj': page_obj})

@login_required(login_url='admin_login')
def edit_product(request,id):
    if not request.user.is_superuser:
        return redirect('admin_login')

    beta = get_object_or_404(Product,id=id)
    categories = Categories.objects.filter(is_active=True)
    
    error = None
    try :
        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            category_id = request.POST.get('category_id')
            offer = request.POST.get('offer')
            image1 = request.FILES.get('image1')
            image2 = request.FILES.get('image2')
            image3 = request.FILES.get('image3')

            if not name:
                messages.error(request, 'Product name is required.')
                return redirect('edit_product', id=beta.id)

            if Product.objects.filter(name__iexact=name).exclude(id=beta.id).exists():
                messages.error(request, 'Another product with this name already exists.')
                return redirect('edit_product', id=beta.id)

            if not description:
                messages.error(request, 'Description is required.')
                return redirect('edit_product', id=beta.id)

            try:
                price = Decimal(price)
                if price <= 0:
                    messages.error(request, "Price must be greater than zero.")
                    return redirect('edit_product', id=beta.id)
            except InvalidOperation:
                messages.error(request, "Invalid price. Please enter a valid number.")
                return redirect('edit_product', id=beta.id)

            try:
                offer = Decimal(offer) if offer else Decimal(0)
                if offer < 0:
                    messages.error(request, "Offer cannot be negative.")
                    return redirect('edit_product', id=beta.id)
                if offer > 80:
                    messages.error(request, "Offer cannot exceed 80%.")
                    return redirect('edit_product', id=beta.id)
            except InvalidOperation:
                messages.error(request, "Invalid offer. Please enter a valid number.")
                return redirect('edit_product', id=beta.id)

            
            beta.name = name
            beta.description = description
            beta.price = price
            if category_id:
                beta.category = get_object_or_404(Categories,id=category_id)
            beta.offer = offer
            if image1:
                beta.image1 = image1
            if image2:
                beta.image2 = image2

            if image3:
                beta.image3 = image3

            beta.save()
            messages.success(request, "Product updated successfully!")
            return redirect('product_list')

    except Exception as e:
        messages.error(request, f"Error updating product: {str(e)}")
        return redirect('edit_product', id=beta.id)


    return render(request,'admin/edit_product.html',{'item' :beta,'categories':categories})


@login_required(login_url='admin_login')
def product_unlist(request,id):
    if not request.user.is_superuser:
        return redirect('admin_login')

    gamma = get_object_or_404(Product,id=id)
    gamma.is_active = not gamma.is_active

    gamma.save()
    return redirect('product_list')


@login_required(login_url='admin_login')
def variant_list(request,product_id):
    if not request.user.is_superuser:
        return redirect('admin_login')

    product = get_object_or_404(Product,id=product_id)

    item = ProductVariant.objects.filter(product=product)

    return render(request,'admin/variant_list.html',{'variants':item,'product':product})


@login_required(login_url='admin_login')
def add_variant(request, product_id):
    if not request.user.is_superuser:
        return redirect('admin_login')

    product = get_object_or_404(Product, id=product_id)

    sizes = ['XS','S','M','L','XL','XXL',]

    if request.method == "POST":
        size = request.POST.get('size')
        stock = request.POST.get('stock')

        if not stock.isdigit():
            messages.error(request, "Stock should be a number.")
            return redirect('add_variant', product_id=product.id)

        try:
            stock = int(stock)
            ProductVariant.objects.create(product=product, size=size, stock=stock)
            messages.success(request, "Variant added successfully.")
            return redirect('variant_list',product_id=product.id)

        except Exception as e:
            print(f"add_variant error: {e}")
            messages.error(request, f"Failed to add variant. Error: {e}")
            return redirect('add_variant',product_id=product.id)

    return render(request, 'admin/add_variant.html', {'product': product,'sizes':sizes})


@login_required(login_url='admin_login')
def edit_variant(request,id,product_id):
    if not request.user.is_superuser:
        return redirect('admin_login')

    product = get_object_or_404(Product,id=product_id)
    prodvar = get_object_or_404(ProductVariant,id=id)
    error=""
    sizes = ['XS','S','M','L','XL','XXL']


    if request.method=='POST':
        size = request.POST.get('size')
        stock=request.POST.get('stock')

        if not stock.isdigit() or int(stock)<0:
            error = "stock must be positive number"
        if error:
            return render(request,'admin/edit_variant.html',{'item':prodvar,'error':error})
            

        prodvar.size = size
        prodvar.stock = int(stock)

        prodvar.save()
        return redirect('variant_list',product_id=prodvar.product.id)

    return render(request,'admin/edit_variant.html',{'item':prodvar,'sizes':sizes})


def shop_list(request):
    prod = Product.objects.filter(is_active=True,category_id__is_active=True)
    categories=Categories.objects.filter(is_active=True)

    category_id=request.GET.get('category','')
    if category_id:
        prod=prod.filter(category_id=category_id)

    min_price=request.GET.get('min_price','')
    max_price=request.GET.get('max_price','')
    if min_price:
        prod=prod.filter(price__gte=min_price)
    if max_price:
        prod=prod.filter(price__lte=max_price)

    search = request.GET.get('search','')
    if search:
        prod=prod.filter(name__icontains=search)

    sort_by=request.GET.get('sort','')
    if sort_by=="low_to_high":
        prod=prod.order_by('price')
    elif sort_by=="high_to_low":
        prod=prod.order_by('-price')
    elif sort_by=="aA-zZ":
        prod=prod.order_by('name')
    elif sort_by=="zZ-aA":
        prod=prod.order_by('-name')

    paginator = Paginator(prod,6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'shop.html',{'page_obj':page_obj,'search':search,'sort_by':sort_by,'categories':categories,'selected_category':category_id,'min_price':min_price,'max_price':max_price})

def product_details(request,id):
    data = get_object_or_404(Product,id=id)
    size_variant = data.variant.all().values('size','stock')

    for variant in size_variant:
        print(f"Size: {variant['size']}, Stock: {variant['stock']}")


    return render(request,'product_details.html',{'data':data,'item':size_variant})