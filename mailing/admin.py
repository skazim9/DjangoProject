from django.contrib import admin

from mailing.models import Recipient, Message
@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email")
    search_fields = ('full_name', 'email')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("topic",)
    ordering = ("topic",)
    search_fields = ("topic", "text")