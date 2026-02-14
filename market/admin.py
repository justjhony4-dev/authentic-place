from django.contrib import admin
from market.models import Category, Vendor, Product


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user',
        'subscription_plan',
        'is_verified',
        'created_at'
    )
    list_filter = ('subscription_plan', 'is_verified')
    search_fields = ('name', 'whatsapp_number')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'slug')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'is_active')
    list_filter = ('vendor', 'category')
    search_fields = ('name',)
