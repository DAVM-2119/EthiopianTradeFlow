from django.contrib import admin
from .models import CustomsDocument

@admin.register(CustomsDocument)
class CustomsDocumentAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'document_type', 'document_number', 'clearance_status', 'validation_status', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'clearance_status', 'validation_status')
    search_fields = ('shipment__id', 'document_number', 'original_filename')
