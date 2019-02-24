from django.contrib import admin

# Register your models here.
from gameapi.models import Token


class TokenAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Token, TokenAdmin)
