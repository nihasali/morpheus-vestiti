from django.urls import path,include
from . import views

urlpatterns = [
    path('user/login/',views.Loginpage,name='loginpage'),
    path('signup/',views.Signuppage,name='signup'),
    path('',views.Homepage,name='homepage'),
    path('verify-otp/',views.verify_otp, name='verify_otp'),
    path('resend-otp/',views.resend_otp, name='resend_otp'),
    path('logout/',views.logout_user, name='logout_user'),
    path('forgot-password/',views.forgot_password,name='forgot_password'),
    path('forgot-password/verify/',views.forgot_otp_verify,name='forgot_otp_verify'),
    path('set-new/password/<int:user_id>',views.set_new_password,name='set_new_password'),
    path("accounts/", include("allauth.urls")),
]
