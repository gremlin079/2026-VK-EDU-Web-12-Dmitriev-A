from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, SignUpForm

from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import Profile


def get_safe_redirect(request, url):
    if url and url_has_allowed_host_and_scheme(
        url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return url

    return reverse('index')


def login_view(request):
    next_url = (
        request.POST.get('next')
        or request.GET.get('next')
        or ''
    )

    form = LoginForm(
        request=request,
        data=request.POST if request.method == 'POST' else None,
    )

    if request.method == 'POST' and form.is_valid():

        auth_login(request, form.get_user())

        return redirect(
            get_safe_redirect(request, next_url)
        )

    return render(
        request,
        'core/login.html',
        {
            'form': form,
            'next': next_url,
        }
    )


def signup(request):

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            auth_login(request, user)

            messages.success(
                request,
                'Регистрация успешно завершена!'
            )

            return redirect('index')

    else:
        form = SignUpForm()

    return render(
        request,
        'core/signup.html',
        {'form': form}
    )


@require_POST
def logout_view(request):

    next_url = (
        request.POST.get('next')
        or request.META.get('HTTP_REFERER')
        or ''
    )

    auth_logout(request)

    return redirect(
        get_safe_redirect(request, next_url)
    )


@login_required
def profile(request):
    profile_data = Profile.objects.filter(
        user=request.user
    ).first()

    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Изменения профиля успешно сохранены.'
            )

            return redirect('profile')

    else:
        form = ProfileForm(instance=request.user)

    return render(
        request,
        'core/profile.html',
        {
            'form': form,
            'profile': profile_data,
        }
    )