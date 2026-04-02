import re, logging
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


from .models import Our_Users, Identity
# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create your views here.

class Register(View):
    template_name = 'auth/register.html'
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('Home')
        return render(request, self.template_name, {})
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not username or not password:
            messages.error(request, "All fields are required")
            return redirect('Register')

        if Our_Users.objects.filter(Q(username=username) | Q(email=email)).exists():
            messages.info(request, 'Not Allowed')
            return redirect('Login')
        elif len(password) < 8 or not all(map(lambda pattern: re.search(pattern,password), [r'[a-z]', r'[A-Z]', r'\d'])):
            messages.error(request, 'Passwords must be of 8 digits or more and should contain : A Lowercase Letter, Uppercase Letter and digit.')
            return redirect('Register')
        else:
            try:
                hashed_pw = make_password(password)
                user=Our_Users.objects.create(username=username, email=email,password=hashed_pw)
                identity=Identity.objects.get_or_create(our_users=user)
                messages.success(request,'User registered successfully')
                return redirect('Login')
            except Exception as e:
                logging.error(msg=f'Error - {str(e)}')
                messages.error(request,message='Inconvinience is Regretted. Firing the developer right now.')
                return redirect('Register')

    
class Login(View):
    template_name = 'auth/login.html'
    def get(self, request,*args, **kwargs):
        if request.user.is_authenticated:
            return redirect('Home')
        return render(request,self.template_name)
            
    def post(self,request,*args,**kwargs):
        User_id = request.POST.get('userid')
        Password = request.POST.get('password')
        
        if not User_id or not Password:
            messages.error(request, "All fields are required")
            return redirect('Login')

        try:
            user = Our_Users.objects.get(Q(username = User_id) | Q(email = User_id))
        except Exception as e:
            logging.info(msg=f'Most probably the user isn\'t registered, but Error - {str(e)}')
            messages.info(request,message='Not Allowed')
            return redirect('Login')
        
        if user:
            if check_password(Password,user.password):
                remember_me = request.POST.get('remember')
                if remember_me:
                    request.session.set_expiry(60 * 60 * 24 * 1)
                else:
                    request.session.set_expiry(0) 
                    
                login(request,user)
                return redirect('Home')
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('Login')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('Login')

@login_required()
@require_POST
def user_logout(request):
    logout(request=request)
    return redirect('Login')


    
    