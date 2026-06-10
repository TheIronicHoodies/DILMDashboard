from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

# CustomUser = get_user_model()

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('fullname', 'nickname')}),
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         (None, {'fields': ('fullname', 'nickname')}),
#     )