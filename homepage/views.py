from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
import logging
# Create your views here.

from products.models import Products
from userprofile.models import Userprofile
from authenticate.models import Identity
from cart.models import Cart
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Homepage(View):
    template_name = 'home.html'
    def get(self, request, *args, **kwargs):
         
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user.id)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,created=Identity.objects.get_or_create(session_key=request.session.session_key)
            
        products = Products.objects.all().order_by('-inventory')
        try:
            profile=Userprofile.objects.get(our_users=request.user.id)
        except Exception as e:
            profile=None
            logging.error(msg='The user tried to access profile without logging in')
            
        users_cart = Cart.objects.filter(identity=identity.id).select_related('product')

        context = {
            'base':request.user,
            'profile':profile,
            'products' : products,
            'cart_items':users_cart
        }
        return render(request, self.template_name, context)
    
    