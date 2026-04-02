from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

# Create your views here.
from Checkout.models import CheckoutItems, Checkout
from authenticate.models import Identity
from userprofile.models import Userprofile

class Orders(View):
    template_name = 'orders/order_view.html'
    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,created=Identity.objects.get_or_create(session_key=request.session.session_key)
        orders = CheckoutItems.objects.filter(identity=identity.id).all()
        profile = Userprofile.objects.filter(our_users=request.user.id).first()
        context = {
            'orders': orders,
            'base':request.user,
            'profile':profile
        }
        return render(request,self.template_name,context)
    
class OrdersDetials(View):
    template_name = 'orders/order_detail_view.html'
    def get(self,request,id=None,*args,**kwargs):
        if request.user.is_authenticated:
            identity,created=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,created=Identity.objects.get_or_create(session_key=request.session.session_key)
        order=Checkout.objects.filter(identity=identity.id,pk=id)
        items=CheckoutItems.objects.filter(~Q(order_status='Cancelled'),checkout=id,identity=identity.id)
        profile = Userprofile.objects.filter(our_users=request.user.id).first()

        context = {
            'order':order,
            'items':items,
            'base':request.user,
            'profile':profile
        }
        return render(request,self.template_name,context)
    
@require_POST
@login_required()
def cancel_order(request,*args,**kwargs):
    if request.user.is_authenticated:
        identity,created=Identity.objects.get_or_create(our_users=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        identity,created=Identity.objects.get_or_create(session_key=request.session.session_key)
        
    checkout_id=request.POST.get('checkout_id')
    selected_ids=list(map(int,request.POST.getlist('selected_items[]')))
    
    checkout=Checkout.objects.get(pk=checkout_id)
    
    items_to_cancel=checkout.items.filter(identity=identity.id,pk__in=selected_ids)
    for item in items_to_cancel:
        item.order_status='Cancelled'
        item.product.inventory += item.quantity
        item.product.save()
        item.save()
    
    existing_items=checkout.items.exclude(order_status='Cancelled')
    if existing_items.exists():
        checkout.order_status='Partially Cancelled'
    else:
        checkout.order_status='Cancelled'
    
    checkout.save()
    
    return redirect('orders')


@login_required
def filter_orders(request, *args, **kwargs):
    template_name='orders/order_view.html'
    
    if request.user.is_authenticated:
        identity,_=Identity.objects.get_or_create(our_users=request.user)
    else:
        return redirect('Login')
    
    orders=CheckoutItems.objects.filter(identity=identity)
    time_query=None
    status=None
    
    status=request.GET.getlist('status')
    if status:
        orders=orders.filter(checkout__order_status__in=status)
    
    selected_time=request.GET.getlist('time')
    
    if selected_time:
        time_query = Q()

        for t in selected_time:
            if t == "30days":
                last_30 = datetime.now() - timedelta(days=30)
                time_query |= Q(checkout__created_at__gte=last_30)

            elif t == "2024":
                time_query |= Q(checkout__created_at__year=2024)

            elif t == "2023":
                time_query |= Q(checkout__created_at__year=2023)

            elif t == "older":
                time_query |= Q(checkout__created_at__year__lt=2023)
                
        orders=orders.filter(time_query)
    
    profile = Userprofile.objects.filter(our_users=request.user.id).first()
    
    context = {
        'orders':orders,
        'base':request.user,
        'profile':profile
    }
    return render(request,template_name,context)

        
    
