from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Order, OrderItem, Promotion, Brand

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active', 'image_preview']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 8px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_display', 'stock', 'is_featured', 'is_bestseller', 'is_active', 'image_preview']
    list_filter = ['category', 'is_featured', 'is_bestseller', 'is_flash_sale', 'is_active']
    list_editable = ['stock', 'is_featured', 'is_bestseller', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Prix et stock', {
            'fields': ('price', 'old_price', 'stock')
        }),
        ('Images', {
            'fields': ('image', 'image_2', 'image_3', 'image_4')
        }),
        ('Variantes', {
            'fields': ('sizes', 'colors')
        }),
        ('Mise en avant', {
            'fields': ('is_featured', 'is_bestseller', 'is_flash_sale', 'flash_sale_end', 'is_active')
        }),
    )

    def price_display(self, obj):
        if obj.old_price:
            return format_html('<span style="text-decoration: line-through; color: #999;">{} FCFA</span> <strong style="color: #c41e3a;">{} FCFA</strong>', 
                             f"{obj.old_price:,}".replace(",", " "),
                             f"{obj.price:,}".replace(",", " "))
        return format_html('<strong>{} FCFA</strong>', f"{obj.price:,}".replace(",", " "))
    price_display.short_description = "Prix"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 8px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'price', 'quantity', 'size', 'color', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'customer_phone', 'customer_city', 'total_display', 'status', 'created_at']
    list_filter = ['status', 'customer_city', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    list_editable = ['status']

    def total_display(self, obj):
        return format_html('<strong>{} FCFA</strong>', f"{obj.total_amount:,}".replace(",", " "))
    total_display.short_description = "Total"


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order']
    list_editable = ['is_active', 'order']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'order', 'logo_preview']
    list_editable = ['is_active', 'order']

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="80" height="40" style="object-fit: contain;" />', obj.logo.url)
        return "-"
    logo_preview.short_description = "Logo"
