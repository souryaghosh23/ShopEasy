from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages

from datetime import datetime
import logging

from products.models import Products, Category
from authenticate.models import Identity

logger=logging.Logger(__name__)

class Seller(View):
    template_name="seller/seller_home.html"
    def get(self,request,*args,**kwargs):
        return render(request,self.template_name,{})
        
class SellerDashboard(View):
    template_name="seller/seller_dashboard.html"
    def get(self,request,*args,**kwargs):
        
        categories=Category.objects.all()
        
        context={
            'categories':categories,
        }
        return render(request,self.template_name,context)

    def post(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            identity,_=Identity.objects.get_or_create(our_users=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            identity,_=Identity.objects.get_or_create(session_key=request.session.session_key)
            
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        discounted_price = request.POST.get('discounted_price')
        quantity = request.POST.get("quantity")
        expiry_date = request.POST.get("expiry_date")
        image = request.FILES.get("image")
        category_id=request.POST.get('category')

        # Basic validation
        if not name or not price or not quantity or not image or not category_id:
            messages.error(request, message="Please fill all required fields.")
            return redirect("seller_dashboard")

        try:
            category=Category.objects.get(id=category_id)       
        except Exception as e:
            logger.error(msg=str(e))
            messages.error(request, message="Please try again.")
            return redirect("seller_dashboard")

        products,state=Products.objects.get_or_create(name=name,description=description,original_price=price,discounted_price=discounted_price,inventory=quantity,image=image,category=category)
        if state:
            products.name=name
            products.description=description
            products.original_price=price
            products.discounted_price=discounted_price
            products.inventory=quantity
            products.image=image
            products.category=category
            
            products.save()
            products.save()
            
            return redirect('Home')

        return render(request, "seller/create_product.html")

        
        
        