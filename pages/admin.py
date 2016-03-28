from django.contrib import admin

# Register your models here.

from .models import Page, Content

admin.site.register(Page)
admin.site.register(Content)
