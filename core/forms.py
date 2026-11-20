from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)

from .models import Profile


User = get_user_model()


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'

        self.fields['username'].widget.attrs.update({
            'placeholder': 'Введите логин',
            'autocomplete': 'username',
        })

        self.fields['password'].widget.attrs.update({
            'placeholder': 'Введите пароль',
            'autocomplete': 'current-password',
        })


class SignUpForm(UserCreationForm):

    email = forms.EmailField(
        label='Электронная почта',
        required=True,
    )

    first_name = forms.CharField(
        label='Имя',
        max_length=150,
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Логин'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повторите пароль'

        self.fields['username'].widget.attrs.update({
            'placeholder': 'Придумайте логин',
            'autocomplete': 'username',
        })

        self.fields['email'].widget.attrs.update({
            'placeholder': 'example@mail.com',
        })

        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'Ваше имя',
        })

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Пользователь с такой почтой уже зарегистрирован.'
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']

        if commit:
            user.save()

            Profile.objects.get_or_create(
                user=user
            )

        return user

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label='Электронная почта'
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        labels = {
            'username': 'Ник',
            'email': 'Электронная почта',
        }

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(
            username__iexact=username
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                'Пользователь с таким ником уже существует.'
            )

        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(
            email__iexact=email
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                'Пользователь с такой почтой уже существует.'
            )

        return email