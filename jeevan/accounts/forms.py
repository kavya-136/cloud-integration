import re

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import CustomUser


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, strip=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput, strip=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username.isalnum():
            raise ValidationError('Username can only contain letters and numbers.')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError('This username is already in use.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError('This email is already in use.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Passwords do not match.')

        if password:
            if len(password) < 8:
                self.add_error('password', 'Password must be at least 8 characters long.')
            if not re.search(r'[A-Z]', password):
                self.add_error('password', 'Password must include at least one uppercase letter.')
            if not re.search(r'[a-z]', password):
                self.add_error('password', 'Password must include at least one lowercase letter.')
            if not re.search(r'\d', password):
                self.add_error('password', 'Password must include at least one number.')

            try:
                validate_password(password, self.instance)
            except ValidationError as exc:
                self.add_error('password', exc)

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, strip=False)
    remember_me = forms.BooleanField(required=False)
