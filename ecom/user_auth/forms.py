from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import re

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

    def clean_password1(self):
        password =self.cleaned_data.get("password1")

        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

        if not re.match(pattern,password):
            raise forms.ValidationError(
                "Password must be at least 8 characters long, "
                "contain at least 1 uppercase letter, 1 lowercase letter, "
                "1 number, and 1 special character (@$!%*?&)."
            )
        return password
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()

        if len(username) < 4:
            raise forms.ValidationError("username should have 4 character long")

        if " " in username:
            raise forms.ValidationError("username cannot contain space")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email','').strip()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('this email is aready exist')
        return email


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)
