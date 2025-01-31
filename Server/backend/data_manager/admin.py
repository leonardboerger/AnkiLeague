from django.contrib import admin
from .models import Data

# Register your models here.
@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'reviews', 'time', 'streak', 'retention')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'date')
    date_hierarchy = 'date'