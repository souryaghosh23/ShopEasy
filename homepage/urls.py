from django.urls import path, include

from authenticate.views import Register, Login, user_logout #authenticate app
from .views import Homepage #homepage app
from products.views import Products_Overall, Products_Detail # products app
from cart.views import go_to_cart, update_cart_quantity,remove_cart #cart app
from Checkout.views import Checkout_Data, Checkout_View, update_checkout_quantity, make_payment,verify_payment, uncheck, handle_identity_upgrade
from address.views import User_Address, Edit_Address, delete_address
from userprofile.views import ProfileView
from orders.views import Orders, OrdersDetials,cancel_order,filter_orders
from seller.views import Seller,SellerDashboard

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
   path("logout/",user_logout,name='Logout'),
   path("register/", Register.as_view(), name='Register'), #authenticate app
   path("login/", Login.as_view(), name = 'Login'), #authenticate app
   
   path("",Homepage.as_view(),name='Home'), # authenticate app
   path("seller/",Seller.as_view(),name='seller'),
   path("createproducts/",SellerDashboard.as_view(),name='seller_dashboard'),
   path("new_arrivals/", Products_Overall.as_view(), name='Products'),#Products app
   path("products_detail/<int:id>", Products_Detail.as_view(),name='Products_Detail'),#Products app
   
   path("cart/<int:id>", go_to_cart, name = "AddToCart"),#Cart Func
   path("update-cart/", update_cart_quantity, name='UpdateCart'),#Cart Func
   path("remove-cart/", remove_cart, name = 'RemoveCart'),
   
   path("internal/", Checkout_Data.as_view(), name='Checkout_Data'),
   path("checkout/", Checkout_View.as_view(), name='Checkout_View'),
   path("chkout_qtity_updt/", update_checkout_quantity, name="Checkout_Quantity_Update"),
   path("uncheck/", uncheck, name="Uncheck_Items"),
   path("checkout/checkout_login",handle_identity_upgrade,name='checkout_login'),
   
   path("address/", User_Address.as_view(), name="Address"),
   path("edit_address/<int:id>/", Edit_Address.as_view(), name='edit_address'),
   path("delete_address/<int:id>/", delete_address, name="DeleteAddress"),
   
   path("payment/",make_payment, name="Make_Payment"),
   path("verify-payment/", verify_payment, name="verify_payment"),
   
   path("profile/", ProfileView.as_view(), name="profile"),
   path("orders/",Orders.as_view(),name="orders"),
   path("order/<int:id>",OrdersDetials.as_view(),name='order_detail'),
   path("order/",cancel_order,name='cancel'),
   path("orders/filter/", filter_orders, name="filter_orders"),
   # path("accounts/", include("django.contrib.auth.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
