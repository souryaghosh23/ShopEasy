from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Q
import logging

from .models import Products, Category
from cart.models import Cart
from authenticate.models import Identity
from userprofile.models import Userprofile
# Create your views here.
logger=logging.Logger(__name__)

class Products_Overall(View):
    template_name = 'products/flexible.html'
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user) 
        else:
            if not request.session.session_key:
                request.session.create()
            identity,state=Identity.objects.get_or_create(session_key=request.session.session_key)
        
        category=request.GET.get('category')
        try:
            all_products = Products.objects.filter(category__name__iexact=category.lower()).order_by('-inventory')
        except Exception as e:
            all_products=Products.objects.all().order_by('-inventory')
            logger.error(msg=str(e))
            
        try:
            profile=Userprofile.objects.get(our_users=request.user.id)
        except Exception as e:
            profile=None
            logger.log(level=logging.DEBUG,msg=f'Couldn\'t get the user\'s profile. For some reason. Error - {str(e)}')
            
        users_cart = Cart.objects.filter(identity=identity.id).select_related('product')
        
        context = {
            'profile':profile,
            'base':request.user,
            'products' : all_products,
            'cart_items':users_cart
        }
                
        return render(request, self.template_name, context)
    
    def post (self, request, *args, **kwargs):
        all_products = Products.objects.all().order_by('-inventory')
        
        context = {
            'products' : all_products
        }
        
        return render(request, self.template_name, context)
    
class Products_Detail(View):
    template_name = 'products/detail.html'
    def get(self, request, id = None, *args, **kwargs):

        try:
            product = Products.objects.get(id=id)
        except Products.DoesNotExist:
            messages.error(request,"The product does not exist")
            return redirect('Products')
        
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
        
        try:
            profile=Userprofile.objects.get(our_users=request.user.id)
        except Exception as e:
            profile=None
            logger.log(level=logging.DEBUG,msg=f'Couldn\'t get the user\'s profile. For some reason or error {e}')
        
        users_cart = Cart.objects.filter(identity=identity.id).select_related('product')
        
        context = {
            'product' : product,
            'open_cart' : request.session.pop('open_cart',False),
            'cart_items' : users_cart,
            'base':request.user,
            'profile':profile
        }
        
        return render(request, self.template_name, context)
    
    def post (self, request, *args, **kwargs):
        all_products = Products.objects.all().order_by('-inventory')
        
        context = {
            'product' : all_products
        }
        
        return render(request, self.template_name, context)
