from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from order.models import Order,OrderItem
from product.models import Product
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from django.utils.timezone import now
import datetime
import pandas as pd
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.utils.timezone import now
from datetime import datetime, timedelta
import calendar
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from collections import defaultdict
import json
from django.core.paginator import Paginator


@login_required(login_url='admin_login')
def user_listing(request):
    if not request.user.is_superuser:
        return redirect('admin_login')

    User = get_user_model()

    search = request.GET.get('search','')
    if search:
        users=User.objects.filter(
            Q(username__icontains=search) | Q(email__icontains=search)
        )
    else:
        users=User.objects.order_by('-id').all()


    return render(request,'admin/user_list.html',{'item':users})

@login_required(login_url='admin_login')
def block_user(request,id):
    if not request.user.is_superuser:
        return redirect('admin_login')

    User = get_user_model()
    alpha = get_object_or_404(User,id=id)
    if alpha.is_active==True:
        User.objects.filter(id=alpha.id).update(is_active=False)
    else:
        User.objects.filter(id=alpha.id).update(is_active=True)

    return redirect('user_listing')

def admin_login(request):

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method=='POST':
        name = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username=name,password=password)

        if user is not None and user.is_superuser:
            login(request,user)
            return redirect('admin_dashboard')
            
        else:
            messages.error(request,"invalid credentials")

    return render(request,'admin/login.html')



@login_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    return redirect('admin_login')


def filter_orders_by_date(filter_type, start_date=None, end_date=None):
    today = datetime.now().date()

    if filter_type == 'daily':
        return Order.objects.filter(created_at__date=today)
    
    elif filter_type == 'weekly':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return Order.objects.filter(created_at__date__range=[start_of_week, end_of_week])

    elif filter_type == 'yearly':
        return Order.objects.filter(created_at__year=today.year)

    elif filter_type == 'custom' and start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            return Order.objects.filter(created_at__date__range=[start_date, end_date])
        except ValueError: 
            return Order.objects.none()
    
    else:
        return Order.objects.all()

def sales_report_view(request):
    
    filter_type = request.GET.get("filter", None)
    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", None)
    show_all = request.GET.get("show_all", None)


    orders = filter_orders_by_date(filter_type,start_date,end_date)

    if not show_all:
        paginator = Paginator(orders, 10)
        page_number = request.GET.get("page")
        orders = paginator.get_page(page_number)

    context = {
        'orders':orders,
        "filter_type": filter_type if filter_type else "",
        "start_date": start_date if start_date else "",
        "end_date": end_date if end_date else "",
        "show_all": show_all,
    }
    return render(request, "admin/sales_report.html", context)


def download_sales_report_excel(request):
    filter_type = request.GET.get("filter", None)
    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", None)

    orders = filter_orders_by_date(filter_type, start_date, end_date)

    data = []
    for order in orders:
        data.append([
            order.id,
            order.user.username,
            order.payment_method,
            order.real_price,
            order.discount_amount,
            order.total_price,
            order.status,
            order.created_at.strftime("%Y-%m-%d")
        ])

    df = pd.DataFrame(data, columns=["Order ID", "Customer", "Payment Method", "Total Price", "Discount", "Final Price", "Status", "Date"])


    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'


    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    return response


def download_sales_report_pdf(request):
    filter_type = request.GET.get("filter", None)
    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", None)

    orders = filter_orders_by_date(filter_type, start_date, end_date)
    total_order_value = sum(order.total_price for order in orders)
    generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'


    p = canvas.Canvas(response)


    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 820, "Morpheus Vestiti - Report") 
    p.setFont("Helvetica", 12)
    

    p.drawString(400, 820, f"Generated: {generated_date}")


    y = 780
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "Order ID")
    p.drawString(180, y, "Customer")
    p.drawString(300, y, "Total Price")
    p.drawString(400, y, "Date")
    
    y -= 20
    p.setFont("Helvetica", 12)


    if not orders:
        p.drawString(200, y, "No orders found for the selected criteria.")
    else:
        for order in orders:
            p.drawString(100, y, str(order.id))
            p.drawString(180, y, order.user.username)
            p.drawString(300, y, f"${order.total_price:.2f}")
            p.drawString(400, y, order.created_at.strftime("%Y-%m-%d"))
            y -= 20


    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y-20, f"Total Order Value: ${total_order_value:.2f}")

    p.showPage()
    p.save()
    return response




def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
        
    total_revenue = Order.objects.filter(status="completed").aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_orders = Order.objects.exclude(status="In Transit").count()
    total_products = Product.objects.count()

    top_products = OrderItem.objects.filter(
        order__status = "completed"
    ).values('product__id','product__name','product__image1').annotate(
        total_quantity = Sum('quantity')
    ).order_by('-total_quantity')[:3]

    top_categories = OrderItem.objects.filter(
        order__status = 'completed'
    ).values('product__category_id__id','product__category_id__name','product__category_id__image').annotate(
        total_quantity = Sum('quantity')
    ).order_by('-total_quantity')[:3]

    
    current_month = now().month
    current_year = now().year
    
    monthly_earning = Order.objects.filter(
        created_at__year=current_year, 
        created_at__month=current_month, 
        status="completed"
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    latest_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    new_users = User.objects.order_by('-date_joined')[:5]
    
    available_years = Order.objects.dates('created_at', 'year').values_list('created_at__year', flat=True)
    available_years = sorted(list(set(available_years)))
    
    if not available_years:
        available_years = [current_year]
    

    chart_filter = request.GET.get('filter', 'monthly')
    chart_year = int(request.GET.get('year', current_year))
    chart_month = int(request.GET.get('month', current_month))
    

    chart_data, chart_labels, chart_values = get_chart_data(chart_filter, chart_year, chart_month)
    

    chart_data_json = json.dumps(chart_data)
    chart_labels_json = json.dumps(chart_labels)
    chart_values_json = json.dumps(chart_values)
    
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'monthly_earning': monthly_earning,
        'latest_orders': latest_orders,
        'new_users': new_users,
        'available_years': available_years,
        'current_year': current_year,
        'current_month': current_month,
        'chart_filter': chart_filter,
        'chart_data_json': chart_data_json,
        'chart_labels_json': chart_labels_json,
        'chart_values_json': chart_values_json,
        'top_products':top_products,
        'top_categories':top_categories,
    }
    
    return render(request, 'admin/index.html', context)





def get_chart_data(filter_type, year, month=None):
    """Generate chart data based on filter type"""
    data = {}
    labels = []
    values = []
    
    if filter_type == 'yearly':
        
        years = list(range(year-4, year+1))
        for y in years:
            yearly_sum = Order.objects.filter(
                created_at__year=y,
                status="completed"
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0
            
            labels.append(str(y))
            values.append(float(yearly_sum))
    
    elif filter_type == 'monthly':
        
        for m in range(1, 13):
            monthly_sum = Order.objects.filter(
                created_at__year=year,
                created_at__month=m,
                status="completed"
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0
            
            month_name = calendar.month_name[m]
            labels.append(month_name)
            values.append(float(monthly_sum))
    
    elif filter_type == 'weekly':
        
        
        for week in range(1, 53):
            start_date = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w').date()
            end_date = start_date + timedelta(days=6)
            
            weekly_sum = Order.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
                status="completed"
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0
            
            labels.append(f'Week {week}')
            values.append(float(weekly_sum))
    
    elif filter_type == 'daily':
        
        _, num_days = calendar.monthrange(year, month)
        
        for day in range(1, num_days + 1):
            daily_sum = Order.objects.filter(
                created_at__year=year,
                created_at__month=month,
                created_at__day=day,
                status="completed"
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0
            
            labels.append(f'{day}')
            values.append(float(daily_sum))
    
    data = {
        'labels': labels,
        'values': values
    }
    
    return data, labels, values

def chart_data_api(request):
    """API endpoint to get chart data for AJAX requests"""
    filter_type = request.GET.get('filter', 'monthly')
    year = int(request.GET.get('year', now().year))
    month = int(request.GET.get('month', now().month))
    
    data, labels, values = get_chart_data(filter_type, year, month)
    
    return JsonResponse({
        'labels': labels,
        'values': values
    })