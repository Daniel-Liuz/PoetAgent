# E:\Program\poetry_project\core\forms.py

from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='请输入您的邮箱，用于找回密码。')
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("该邮箱地址已经被注册，请使用其他邮箱。")
        return email

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.CharField(
        label="用户名或邮箱地址",
        max_length=254,
        widget=forms.TextInput(attrs={'autocomplete': 'username'})
    )
    def get_users(self, email):
        identifier = self.cleaned_data.get('email')
        users = User.objects.filter(username__iexact=identifier, is_active=True)
        if not users.exists():
            users = User.objects.filter(email__iexact=identifier, is_active=True)
        return users
