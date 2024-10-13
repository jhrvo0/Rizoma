from django.contrib import admin
from .models import Agricultor, Campo

class CampoInline(admin.TabularInline):
    model = Agricultor.campos.through
    extra = 1

@admin.register(Agricultor)
class AgricultorAdmin(admin.ModelAdmin):
    list_display = ['email', 'username']
    search_fields = ['email', 'username']
    inlines = [CampoInline]

@admin.register(Campo)
class CampoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']