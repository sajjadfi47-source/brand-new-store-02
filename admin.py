from django.contrib import admin
from .models import Category,Product,ProductImage,StoreSettings,Order,OrderItem
class ProductImageInline(admin.TabularInline):
 model=ProductImage; extra=1
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
 list_display=("name","category","price","old_price","stock","active","featured")
 list_filter=("category","active","featured"); search_fields=("name","description"); prepopulated_fields={"slug":("name",)}
 inlines=[ProductImageInline]
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin): list_display=("name","active"); prepopulated_fields={"slug":("name",)}
class OrderItemInline(admin.TabularInline):
 model=OrderItem; extra=0; can_delete=False; readonly_fields=("product_name","unit_price","quantity","size","color")
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
 list_display=("order_id","customer_name","phone","total","payment_method","status","created_at")
 list_filter=("status","payment_method","created_at"); search_fields=("order_id","customer_name","phone")
 readonly_fields=("order_id","customer_name","phone","district","area","address","note","payment_method","subtotal","delivery_charge","total","created_at")
 inlines=[OrderItemInline]
@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin): list_display=("name","phone","whatsapp")
