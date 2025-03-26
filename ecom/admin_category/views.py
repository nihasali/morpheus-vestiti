from django.shortcuts import render,redirect,get_object_or_404
from .models import Categories
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages


@login_required(login_url='admin_login')
def category_list(request):

    item = Categories.objects.order_by('id').all()
    return render(request,'admin/category.html',{'item':item})


@login_required(login_url='admin_login')
def create_category(request):

    item = Categories.objects.order_by('-id').all()

    if request.method =='POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        cat_offer = request.POST.get('cat_offer','').strip()
        image = request.FILES.get('image')

        print(f"Received cat_offer: {cat_offer}")

        if not name:
            messages.error(request, 'Category name is required.')
            return redirect('create_category')

        if not description:
            messages.error(request, 'Description is required.')
            return redirect('create_category')

        if Categories.objects.filter(name__iexact=name).exists():
            messages.error(request,'This category already exists!.')
            return redirect('create_category')

        try:
            cat_offer = Decimal(cat_offer) if cat_offer else Decimal(0)
            if cat_offer < 0:
                messages.error(request, "Offer value cannot be negative.")
                return redirect('create_category')
            if cat_offer > 80:
                messages.error(request, "Offer value cannot exceed 80%.")
                return redirect('create_category')
        except ValueError:
            messages.error(request, "Invalid offer value. Please enter numbers only.")
            return redirect('create_category')

        print(f"Converted cat_offer: {cat_offer}")

        if not image:
            messages.error(request, "Category image is required.")
            return redirect('create_category')

        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if image:
            if image.content_type not in allowed_types:
                messages.error(request, "Only JPEG, PNG, and GIF image files are allowed!")
                return redirect('create_category')



        category = Categories.objects.create(name=name,description=description,cat_offer=cat_offer,image=image)
        category.save()

        products = category.product.all()
        for product in products:
            product.save() 

        return redirect('category_list')

    return render(request,'admin/category.html',{'item':item})


@login_required(login_url='admin_login')
def edit_category(request,id):
    
    category = get_object_or_404(Categories,id=id)
    item = Categories.objects.order_by('id').all()

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        cat_offer = request.POST.get('cat_offer')
        image = request.FILES.get('image')

        if not name:
            messages.error(request, 'Category name is required.')
            return redirect('edit_category', id=category.id)

        if not description:
            messages.error(request, 'Description is required.')
            return redirect('edit_category', id=category.id)

        if Categories.objects.filter(name__iexact=name).exclude(id=category.id).exists():
            messages.error(request, 'Another category with this name already exists!')
            return redirect('edit_category', id=category.id)


        try:
            cat_offer = Decimal(cat_offer) if cat_offer else Decimal(0)
            if cat_offer < 0:
                messages.error(request, "Offer value cannot be negative.")
                return redirect('edit_category', id=category.id)
            if cat_offer > 80:
                messages.error(request, "Offer value cannot exceed 80%.")
                return redirect('edit_category', id=category.id)
        except ValueError:
            messages.error(request, "Invalid offer value. Please enter numbers only.")
            return redirect('edit_category', id=category.id)

        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if image:
            if image.content_type not in allowed_types:
                messages.error(request, "Only JPEG, PNG, and GIF image files are allowed!")
                return redirect('edit_category', id=category.id)
            category.image = image


        category.name = name
        category.description = description
        category.cat_offer = cat_offer
        category.save()

        products = category.product.all()
        for product in products:
            product.save() 

        return redirect('category_list')

    return render(request,'admin/edit_category.html',{'item':category})


@login_required(login_url='admin_login')
def unlist_category(request,id):

    category = get_object_or_404(Categories, id=id)

    category.is_active = not category.is_active  
    
    category.save()

    return redirect('category_list')
