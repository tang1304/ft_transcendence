from django import forms
from .models import User

class RegisterForm(forms.ModelForm):
    email

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
