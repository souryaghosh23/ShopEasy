from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse

from .models import Address
from authenticate.models import Our_Users, Identity
# Create your views here.

class User_Address(View):
    template_name = "address/address.html"
    def post(self, request, *args, **kwargs):
        
        phone_number = request.POST.get("phone_number")
        pincode = request.POST.get("pincode")
        city = request.POST.get("city")
        state = request.POST.get("state")
        name = request.POST.get("name")
        house_no_or_street = request.POST.get("house_no_or_street")
        landmark = request.POST.get("landmark")
        is_default = request.POST.get("is_default")
        
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
            
        try:
            Address.objects.create(identity=identity, name=name, phone_number=phone_number, city=city, state=state, pincode=pincode, house_no_or_street= house_no_or_street, landmark=landmark, is_default=is_default)
        except (ValueError, TypeError, IntegrityError, ValidationError):
            return redirect(f"{reverse('Checkout_View')}?msg=error&text=Address could not be added")
        
        return redirect(f"{reverse('Checkout_View')}?msg=success&text=Address added successfully")

class Edit_Address(View):
    def get(self, request, id = None, *args, **kwargs):
        
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
        
        user_address = Address.objects.filter(identity=identity, id =id).first()
        
        if user_address:
            return JsonResponse({
                'status':"success",
                'data' : {
                    'name': user_address.name,
                    'phone_number': user_address.phone_number,
                    'pincode': user_address.pincode,
                    'state': user_address.state,
                    'city': user_address.city,
                    'house_no_or_street': user_address.house_no_or_street,
                    'landmark': user_address.landmark,
                    'is_default': user_address.is_default,
                }
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Address not found'}, status=404)
        
    def post(self, request, id = None, *args, **kwargs):

        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
            
        user_address = Address.objects.filter(identity=identity, id =id).first()
        
        if user_address:
            fields = ['name', 'phone_number', 'pincode', 'state', 'city', 'house_no_or_street', 'landmark', 'is_default']
            for field in fields:
                setattr(user_address, field, request.POST.get(field))
            user_address.save()
            
            return redirect(f"{reverse('Checkout_View')}?msg=success&text=Address saved successfully")
        else:
            return redirect(f"{reverse('Checkout_View')}?msg=error&text=Address couldnt be updated")
            

def delete_address(request, id = None):
    if request.method == "POST":
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
        
        try:
            user_address = Address.objects.filter(identity=identity, id =id).first()
        
            if user_address and user_address.is_default == False:
                user_address.delete()
                return redirect(f"{reverse('Checkout_View')}?msg=success&text=Address deleted successfully")
            else:
                return redirect(f"{reverse('Checkout_View')}?msg=error&text=Address does not exist or Default address cannot be deleted!")
        except Exception:
            return redirect(f"{reverse('Checkout_View')}?msg=error&text=Something went wrong!")
   
