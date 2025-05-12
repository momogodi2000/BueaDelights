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



    # Product listing
    path('product_list/', views.product_list, name='product_list'),
    path('products/<int:product_id>/quick-view/', views.product_quick_view, name='product_quick_view'),
    
    # Cart operations
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    # Checkout and ordering
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/whatsapp/', views.generate_whatsapp_link, name='generate_whatsapp_link'),
    
    # Payment
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/process/<str:transaction_id>/', views.payment_process, name='payment_process'),
    path('payment/webhook/noupia/', views.noupia_webhook, name='noupia_webhook'),
    path('receipt/download/<str:transaction_id>/', views.download_receipt, name='download_receipt'),
    
    # Order history
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),


    
    

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)