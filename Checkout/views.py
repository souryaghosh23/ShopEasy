from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password, check_password
from django.views import View
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction
from django.urls import reverse
from decimal import Decimal
from sequences import get_next_value
from django.db.models import Q

import logging
import razorpay
import datetime
import re

from .models import CheckoutItems, OrderItems, Checkout
from authenticate.models import Identity,Our_Users
from products.models import Products
from cart.models import Cart
from address.models import Address
from root.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
# Create your views here.

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)#linking razorpay 
client = razorpay.Client(auth=(RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET)) 

#taking a snapshot to display the setails in the checkout view. Also re-reouting unecessary load to the checkout model
class Checkout_Data(View):
    def get(self, request, *args, **kwargs):
        
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
            
        try:
            the_product = Cart.objects.filter(identity=identity.id).select_related('product')
        except Exception as e:
            messages.error("The product is not in stock")
            logging.error(msg=f'Error {str}')
            return redirect("Products_Details")
        
        for one_product in the_product:   
            snap_exists = OrderItems.objects.filter(identity=identity.id, product_id = one_product.product.id).first()
            
            if snap_exists:
                snap_exists.quantity = one_product.quantity
                snap_exists.sub_total = one_product.sub_total
                snap_exists.save()
            else:
                OrderItems.objects.create(identity=identity, product_id = one_product.product, 
                                          product_name = one_product.product.name, product_price = one_product.product.discounted_price, 
                                          product_image = one_product.product.image, quantity =  one_product.quantity, 
                                          )
        
        return redirect("Checkout_View")
        
# rendering checkout view at last
class Checkout_View(View):
    template_name = 'exit/checkout.html'
    def get(self, request, *args, **kwargs):
                
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
        
        check_data = OrderItems.objects.filter(identity=identity.id).select_related('product_id')
        address = Address.objects.filter(identity=identity.id)
        
        selected_ones = check_data.filter(selected=True)
        total_amount = sum(item.sub_total for item in selected_ones)       
            
        context = {
            'addresses' : address,
            'total_amount' : total_amount,
            'order_items' : check_data,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):

        payment_method = request.POST.get("payment_method")
        address_id = request.POST.get('address_id')
        
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)

        try:
            address = Address.objects.filter(identity=identity.id, id=address_id).first()
        except (Address.DoesNotExist, ValueError):
            return redirect(f"{reverse('Checkout_View')}?msg=error&text=Invalid Address!")
        
        if payment_method == "razorpay":
            params_dict = {
            'razorpay_order_id': request.POST.get('razorpay_order_id'),
            'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
            'razorpay_signature': request.POST.get('razorpay_signature')
            }

            try:
                client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                return JsonResponse({'status': 'failure', 'reason': 'Invalid signature'})
            
        snap_exists = OrderItems.objects.filter(identity=identity.id).select_related('product_id')
        final_total = Decimal("0.00")
        checkout_list = []
        
        try:   
            with transaction.atomic(): 
                checkout = Checkout.objects.create(
                    identity = identity,
                    invoice=get_next_value("checkout_order_seq"),
                    full_name = address.name,
                    address = address,
                    total_amount = Decimal('0.0'),
                    payment_status = "Completed" if payment_method != "cod" else "Pending",
                    order_status = "Placed",
                    payment_method = payment_method
                )
                
                for one_product in snap_exists:  
                    final_total += one_product.sub_total
                    if one_product.selected:
                        cart = Cart.objects.filter(identity=identity.id, product = one_product.product_id)
                        new_checkout_item = CheckoutItems.objects.create(
                            identity=identity,
                            checkout=checkout,
                            product = one_product.product_id,
                            quantity = one_product.quantity,
                            subtotal = one_product.sub_total,
                            order_status='Placed'
                        )
                        checkout_list.append(new_checkout_item)
                        
                        product = one_product.product_id  # This is your actual Product instance
                        product.inventory -= one_product.quantity
                        product.save()  # ✅ Save the updated product
                        
                        cart.delete()
                    else:
                        continue
                    
                checkout.total_amount=final_total
                checkout.save()
                snap_exists.delete()

                # return redirect('pay_success/success.html', id = checkout.id)
                return redirect('orders')
                    
        except Exception as e:
            logging.error(str(e))
            return redirect(f"{reverse('Checkout_View')}?msg=error&text=Something went wrong!")
        
        

def make_payment(request):
    if request.method == "POST":
        total_amount = request.POST.get('total_amount')
        receipt = f"RCPT-{request.user.id if request.user.is_authenticated else 'GUEST'}-{int(datetime.datetime.now().timestamp())}"
        
        order_data = {
        "amount": int(float(total_amount)) * 100,  # amount in paisa
        "receipt" : receipt,
        "currency": "INR",
        "payment_capture": 1
        }
        
        order = client.order.create(data= order_data)
        return JsonResponse({
            "status": "success",
            "razorpay_order_id": order['id'],
            "razorpay_key_id": RAZORPAY_KEY_ID,
            "amount": order_data['amount'],  # still in paisa
        })
    
def verify_payment(request):
    if request.method == "POST":

        data = request.POST
        params_dict = {
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            return JsonResponse({'status': 'success'})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'failure', 'reason': 'Invalid signature'})
    
# Changing quantity at the checkout page.
@csrf_exempt
def update_checkout_quantity(request):
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
            order_items = OrderItems.objects.filter(identity=identity.id, product_id=product_id).first()
            
            if action == 'increase' and users_cart.quantity < users_cart.product.inventory and users_cart.product.inventory > 0:
                users_cart.quantity += 1
                order_items.quantity += 1
            elif action == 'decrease' and users_cart.quantity > 0 and users_cart.product.inventory > 0:
                users_cart.quantity -= 1
                order_items.quantity -= 1
            if users_cart.quantity <= 0:
                users_cart.delete()
                order_items.delete()
                return JsonResponse({'status': 'ok', 'quantity': 0, 'deleted': True})
            else:
                users_cart.save()
                order_items.save()
                
            return JsonResponse({
                'status' : 'ok',
                'quantity' : users_cart.quantity,
                'subtotal' : users_cart.sub_total
            })
        except Cart.DoesNotExist:
            return JsonResponse({'status' : "Error", "message" : 'Item Not found'})
                    
def uncheck(request) : 
    if request.method == "POST":
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
            
        item_id = request.POST.get("item_id")
        selected = request.POST.get("selected")
        
        try:
            item = OrderItems.objects.filter(identity=identity.id, id=item_id).first()
            item.selected = selected
            item.save()
            return JsonResponse({'status': 'ok'})

        except OrderItems.DoesNotExist:
            pass
        
def handle_identity_upgrade(request):
    if request.method=='POST':
        
        #Fetching the Identity Query set to update
        try:
            identity=Identity.objects.get(session_key=request.session.session_key)
        except Exception as e:
            logging.error(msg=f'Error -- {str(e)}')
            
        #Fetching the cart related to the session key
        cart_items=Cart.objects.filter(identity=identity.id).all()
        
        #Fetching the User ID and Password
        user_id=request.POST.get('user_id')
        password=request.POST.get('password')
        
        if not(user_id or password):
            return messages.error(request,message="Please enter both the /'User Id' and 'Password'")
        
        if len(password) < 8 or not all(map(lambda pattern: re.search(pattern,password), [r'[a-z]', r'[A-Z]', r'\d'])):
            messages.error(request, 'Passwords must be of 8 digits or more and should contain : A Lowercase Letter, Uppercase Letter and digit.')
            return redirect('Checkout_View')
        
        user=Our_Users.objects.filter(Q(email=user_id) | Q(username=user_id)).first()
        if not user:
            hash_pw=make_password(password)
            user=Our_Users.objects.create(username=user_id,email=user_id,password=hash_pw)
            identity.our_users=user
            identity.save()
            login(request,user)
            return redirect('Products')
        else:
            if check_password(password,user.password):
                try:
                    user_identity=Identity.objects.get(our_users=user.id)
                except Exception as e:
                    logging.error(msg=f"Error, {str(e)}")
                    messages.error(request,message='We encountered an Error')
                    return redirect("Checkout_View")
            else:
                logging.error(msg='Wrong password provided by user')
                messages.error(request,message='Wrong Email/Password')
                return redirect('Checkout_View')
        
        try:
            users_cart=Cart.objects.get(identity=user_identity.id)
        except Exception as e:
            logging.error(msg=f'Error - {str(e)}')
            if Cart.DoesNotExist:
                users_cart=None
                
        if not users_cart:
            cart_items_map=[
                {'product':item.product,'quantity':item.quantity,'identity':user_identity} for item in cart_items
            ]
            users_cart_instances=[Cart(**data) for data in cart_items_map]
            created_objects = Cart.objects.bulk_create(users_cart_instances)
            cart_items.delete()
            return redirect('Products')               
        else:
            for items in cart_items:
                if items.product==users_cart.product:
                    users_cart.quantity += items.quantity
                else:
                    users_cart.product=items.product.id
                    users_cart.quantity=items.quantity
            users_cart.save()
            cart_items.delete()
            identity.delete()
        
        login(request,user)
        return redirect('Products')
                
            
