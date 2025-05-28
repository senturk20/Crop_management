from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Crop, Inventory, Sale
from .forms import CropForm, InventoryForm, SaleForm

@login_required
def crop_list(request):
    crops = Crop.objects.filter(user=request.user)
    return render(request, 'management_app/crop_list.html', {'crops': crops})

@login_required
def crop_add(request):
    if request.method == 'POST':
        form = CropForm(request.POST)
        if form.is_valid():
            crop = form.save(commit=False)
            crop.user = request.user
            crop.save()
            return redirect('crop_list')
    else:
        form = CropForm()
    return render(request, 'management_app/crop_form.html', {'form': form})

@login_required
def crop_edit(request, pk):
    crop = get_object_or_404(Crop, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CropForm(request.POST, instance=crop)
        if form.is_valid():
            form.save()
            return redirect('crop_list')
    else:
        form = CropForm(instance=crop)
    return render(request, 'management_app/crop_form.html', {'form': form})

@login_required
def crop_delete(request, pk):
    crop = get_object_or_404(Crop, pk=pk, user=request.user)
    if request.method == 'POST':
        crop.delete()
        return redirect('crop_list')
    return render(request, 'management_app/crop_confirm_delete.html', {'crop': crop})

@login_required
def inventory_list(request):
    inventory_items = Inventory.objects.all()
    return render(request, 'management_app/inventory_list.html', {'inventory_items': inventory_items})

@login_required
def inventory_add(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = InventoryForm()
    return render(request, 'management_app/inventory_form.html', {'form': form})

@login_required
def sale_list(request):
    sales = Sale.objects.all()
    return render(request, 'management_app/sale_list.html', {'sales': sales})

@login_required
def sale_add(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sale_list')
    else:
        form = SaleForm()
    return render(request, 'management_app/sale_form.html', {'form': form})
