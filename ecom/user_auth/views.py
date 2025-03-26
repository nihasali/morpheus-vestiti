from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.models import User
from .forms import SignupForm,LoginForm
from django.contrib import messages
from django.core.mail import send_mail
import random
from product.models import Product
from django.contrib.auth import update_session_auth_hash

def Signuppage(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username= form.cleaned_data.get('username')
            password=form.cleaned_data.get('password1')

            
            otp = random.randint(100000, 999999)
            request.session['otp'] = otp
            request.session['email'] = email
            request.session['password']=password
            request.session['username']=username
            
            send_mail(
                'Email Verification OTP',
                f'Your OTP for email verification is {otp}',
                'your-email@example.com',  
                [email],
                fail_silently=False,
            )

            return redirect('verify_otp')  
        else:
            messages.error(request, "Invalid credentials")

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        email = request.session.get('email')
        username = request.session.get('username')
        password = request.session.get('password')


        print("Username :--------------", username)
        print("Email :----------", email)

        

        if not session_otp or not email or not username:
            messages.error(request, "Session expired. Please sign up again.")
            return redirect('signup')

        if str(entered_otp) == str(session_otp):
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            messages.success(request, "your account created successfully!")
            del request.session['otp']  
            del request.session['email']
            del request.session['username']
            del request.session['password']
            return redirect('homepage')  
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'verify_otp.html')


def resend_otp(request):
    email = request.session.get('email')

    if not email:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect('signup')

    otp = random.randint(100000, 999999)
    request.session['otp'] = otp  
    request.session.modified = True  

    print(f"New OTP: {otp}")  

    try:
        send_mail(
            'Resend OTP - Email Verification',
            f'Your new OTP is {otp}',
            'your-email@example.com',  
            [email],
            fail_silently=False,
        )
        messages.success(request, "A new OTP has been sent to your email.")
    except Exception as e:
        messages.error(request, f"Failed to send OTP. Error: {e}")

    return redirect('verify_otp')

def Loginpage(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                messages.success(request,"you are now login succeesfully")
                return redirect('homepage')
            
            else:
                messages.error(request,"invalid credentials")
    else:
        form = LoginForm()
    return render(request,'signin.html',{'form':form})


def logout_user(request):
    logout(request)
    return redirect('loginpage')




def Homepage(request):
    prods=Product.objects.filter(is_active=True).order_by('-id')[:3]

    return render(request,'index.html',{'item':prods})


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email','')
        user = get_object_or_404(User,email=email)

        if not user:
            messages.error(request,'Email does not exist.please register as a new user')
            return redirect('signup')
        
        else:
            otp = random.randint(100000, 999999)
            request.session['forgot_otp'] = str(otp)
            request.session['user_id'] = user.id

            send_mail(
                'Email Verification OTP',
                f'Your OTP for email verification is {otp}',
                'your-email@example.com',  
                [email],
                fail_silently=False,
            )

            return redirect('forgot_otp_verify')
            
    
    
    return render(request,'forgot_password.html')

def forgot_otp_verify(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('forgot_otp')
        user_id = request.session.get('user_id')

        if not stored_otp or not user_id:
            messages.error(request,'Session time out come again')
            return redirect('forgot_password')

        if entered_otp == str(stored_otp):
            messages.success(request,'OTP verified successfully!.Set a new password')

            del request.session['forgot_otp']

            return redirect('set_new_password',user_id=user_id)

        else:
            messages.error(request,'Invalid OTP! try agin ')


    return render(request,'forgot_otp_verify.html')


def set_new_password(request,user_id):
    user = get_object_or_404(User,id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request,'Confirm password is not match')
            return redirect('set_new_password',user_id=user_id)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request,user)
        messages.success(request,'password changed successfully')
        return redirect('loginpage')

    return render(request,'set_new_password.html')

