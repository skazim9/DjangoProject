from django.contrib import admin

from mailing.models import Recipient
@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email")
    search_fields = ('full_name', 'email')
