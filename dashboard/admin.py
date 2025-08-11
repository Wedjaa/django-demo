from django.contrib.auth.admin import UserAdmin
from .models import DjangoUser
from django.contrib import admin

# print("Registering DjangoUser in admin")
# @admin.register(DjangoUser)
# class DjangoUserAdmin(UserAdmin):
#     list_display = ("username", "email", "get_roles")

#     def get_roles(self, obj):
#         return ", ".join(obj.roles)
#     get_roles.short_description = "Roles"
