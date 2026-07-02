from django.contrib import admin

from .models import (
    Category, Collection, ColorOption, Lead, Material, Order, OrderItem,
    Product, ProductImage, Review,
)


@admin.register(ColorOption)
class ColorOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'finish_type', 'hex', 'order')
    list_filter = ('finish_type',)
    search_fields = ('name',)
    ordering = ('finish_type', 'order', 'name')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_featured', 'order')
    list_filter = ('is_featured',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'material', 'category', 'price', 'is_available', 'is_featured')
    list_filter = ('material', 'category', 'collection', 'is_available', 'is_featured')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('available_colors',)
    inlines = [ProductImageInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'unit_price', 'selected_colors')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer_name', 'customer_phone', 'status', 'payment_status',
        'total_price', 'created_at',
    )
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('customer_name', 'customer_phone', 'customer_email')
    readonly_fields = ('created_at', 'total_price', 'telegram_notified')
    inlines = [OrderItemInline]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'lead_type', 'status', 'source_page', 'created_at')
    list_filter = ('lead_type', 'status')
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('created_at', 'telegram_notified')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'author', 'rating', 'is_published', 'created_at')
    list_filter = ('is_published', 'rating')
    search_fields = ('author', 'product__name')
