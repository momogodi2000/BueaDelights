from django.urls import path
from buea import settings
from . import views
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='homepage'),
      # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    
    # Session management
    path('update_session_activity/', views.update_session_activity, name='update_session_activity'),
    path('check_session_expired/', views.check_session_expired, name='check_session_expired'),
    path('get_csrf_token/', views.get_csrf_token, name='get_csrf_token'),

    # Password management
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_reset_code/', views.verify_reset_code, name='verify_reset_code'),
    path('reset_password/', views.reset_password, name='reset_password'),


    path('adminpanel/', views.adminpanel, name='adminpanel'),
    path('delivery/', views.delivery, name='delivery'),
    path('client/', views.client, name='client'),


    #admin panel
    path('products_list/', views.ProductListView.as_view(), name='products_list'),
    path('add/', views.ProductCreateView.as_view(), name='add_product'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/edit/', views.ProductUpdateView.as_view(), name='edit_product'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='delete_product'),



    ## product shopping
    path('product_list/', views.product_list, name='product_list'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/whatsapp/', views.generate_whatsapp_link, name='generate_whatsapp_link'),
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/process/<str:transaction_id>/', views.payment_process, name='payment_process'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)