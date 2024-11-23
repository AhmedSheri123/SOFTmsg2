from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserSignUpModelForm(forms.ModelForm):
    password = forms.CharField(label='password', max_length=254, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

        widgets = {
            'first_name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'your name...'}),
            'last_name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'your last name...'}),
            'email': forms.EmailInput(attrs={'class':'form-control', 'placeholder':'name@example.com'})
        }

class UserProfileSignUpModelForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'company_name']

        widgets = {
            'phone_number': forms.TextInput(attrs={'class':'form-control', 'placeholder':'phone number'}),
            'company_name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'your company name...'})
        }

class LoginForm(forms.Form):
    email = forms.EmailField(label='email', max_length=254, widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'name@example.com'}))
    password = forms.CharField(label='password', max_length=254, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))
