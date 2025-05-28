from django import forms
from .models import Crop, Inventory, Sale

class CropForm(forms.ModelForm):
    inventory = forms.ModelMultipleChoiceField(
        queryset=Inventory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Crop
        fields = ['name', 'type', 'planting_date', 'harvest_date', 'yield_quantity', 'inventory']

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['name', 'type', 'quantity', 'expiry_date', 'supplier']

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['crop', 'quantity_sold', 'price', 'sale_date']
