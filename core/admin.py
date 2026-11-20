from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    max_num = 1


admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff'
    )

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'avatar')
    search_fields = ('user__username', 'user__email')
    list_filter = ('user__is_staff',)
    list_select_related = ('user',)