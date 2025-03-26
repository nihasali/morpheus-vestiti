from django.urls import path
from . import views

urlpatterns =[
    path('list/',views.user_listing,name='user_listing'),
    path('block_user/<int:id>/',views.block_user,name='block_user'),
    path('',views.admin_login,name = 'admin_login'),
    path('dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('logout/',views.admin_logout,name='admin_logout'),
    path('sales-report/',views.sales_report_view, name='sales_report_view'),
    path('sales-report/excel/',views.download_sales_report_excel, name='download_sales_report_excel'),
    path('sales-report/pdf/',views.download_sales_report_pdf, name='download_sales_report_pdf'),
    path('admin/chart-data/', views.chart_data_api, name='chart_data_api'),
]


