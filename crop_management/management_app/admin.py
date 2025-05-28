from django.contrib import admin
from .models import Supplier, Inventory, Crop, Sale, CropInventory, Alert

admin.site.register(Supplier)
admin.site.register(Inventory)
admin.site.register(Crop)
admin.site.register(Sale)
admin.site.register(CropInventory)
admin.site.register(Alert)
