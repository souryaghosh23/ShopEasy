from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Userprofile
from authenticate.models import Our_Users, Identity
import logging
# Create your views here.

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    template_name = "profile/profile.html"
    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            identity=request.user
        
        try:
            profile=Userprofile.objects.get(our_users=identity.id)
        except Exception as e:
            logging.error(msg=f'The user tried to access profile without logging in or Error - {str(e)}')
            if Userprofile.DoesNotExist:
                profile=None
        
        context = {
            'base':request.user,
            'profile':profile
        }
        return render(request,self.template_name,context)

    def post(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            identity=request.user
                
            f_name=request.POST.get('f_name')
            l_name=request.POST.get('l_name')
            gender=request.POST.get('gender')
            email=request.POST.get('email')
            number=request.POST.get('number')
            
            try:
                profile,status=Userprofile.objects.get_or_create(our_users=identity)
            except Exception as e:
                logging.error(msg=f'We encountered an Error, {str(e)}')
                messages.error(request,message="We encountered a problem")
                return redirect('Home')
            
            if f_name or l_name or gender or number:
                profile.first_name=f_name
                profile.last_name=l_name
                profile.gender=gender
                profile.phone_num=number
                
    
            profile.save()
            
            user=request.user
            if email != user.email:
                user.email=email
                user.save()
            return redirect('profile')
        else:
            return redirect('Login')

        
        
        
            
