from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import logging
# Create your views here.

from .models import Cart
from products.models import Products
from authenticate.models import Identity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
@csrf_exempt
def remove_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id') 
        action = request.POST.get('action')
    
    if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
        
    try:   
        users_cart = Cart.objects.get(identity=identity.id, product = product_id)
        
        if action == 'remove':
            users_cart.delete()
            
        return JsonResponse({
                'status' : 'ok',
                'message' : 'Item Removed'
        })
    except Exception as e:
            logging.error(msg=f"Error - {str(e)}")
            return JsonResponse({'status' : "Error", "message" : 'Item Not found'})
            
@csrf_exempt
def update_cart_quantity(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id') 
        action = request.POST.get('action')
        
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
        
        try:   
            users_cart = Cart.objects.get(identity=identity.id, product = product_id)
            
            if action == 'increase' and users_cart.quantity < users_cart.product.inventory and users_cart.product.inventory > 0:
                users_cart.quantity += 1
            elif action == 'decrease' and users_cart.quantity > 0 and users_cart.product.inventory > 0:
                users_cart.quantity -= 1
            if users_cart.quantity <= 0:
                users_cart.delete()
                return JsonResponse({'status': 'ok', 'quantity': 0, 'deleted': True})
            else:
                users_cart.save()
                
            return JsonResponse({
                'status' : 'ok',
                'quantity' : users_cart.quantity,
                'subtotal' : users_cart.sub_total
            })
        except Exception as e:
            logging.error(msg=f"str({e})")
            return JsonResponse({'status' : "Error", "message" : 'Item Not found'})
        

def go_to_cart(request,id=None, *args, **kwargs):
    if request.method == 'POST': 
        try:
            the_product = Products.objects.get(id=id)
        except Products.DoesNotExist:
            messages.error(request, 'Product is Out Of Stock')
            logging.error(msg=f"str({e})")
            return redirect('Products', id = id)
        
        if the_product.inventory <= 0:
            messages.error(request, 'Product is Out Of Stock')
            return redirect('Products', id = id)
        
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
            
        users_cart = Cart.objects.filter(identity=identity.id).select_related('product')
        existing_cart = None
        if users_cart:
            for items in users_cart:
                if items.product.id == the_product.id:
                    existing_cart = items
                    break
            
        if existing_cart:
            existing_cart.quantity += 1
            existing_cart.save()
        else:
            a=Cart.objects.create(identity=identity, product=the_product, quantity = 1)
                  
        messages.success(request,'The product was added successfully')
        request.session['open_cart'] = True
        return redirect('Products_Detail', id=id)

         

class Cart_View(View):
    def get(self, request, *args, **kwargs):
        
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
        
        cart_items = Cart.objects.filter(identity=identity.id).select_related('product')
        total_sum = sum(item.sub_total for item in cart_items)
        
        context = {
            'cart' : cart_items,
            'total_sum' : total_sum
        }
        
        return render(request, context)
