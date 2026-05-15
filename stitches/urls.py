from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('shop/', views.shop, name='shop'),
    path('signin/', views.signin, name='signin'),
    path('register/', views.register, name='register'),
    path('signout/', views.signout, name='signout'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/increase/<int:product_id>/', views.increase_cart, name='increase_cart'),
    path('cart/decrease/<int:product_id>/', views.decrease_cart, name='decrease_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/', views.order, name='order'),
    path('success/', views.success, name='success'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/add/', views.add_product, name='add_product'),
    path('admin-panel/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin-panel/order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('profile/', views.profile, name='profile'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('admin-panel/edit/<int:product_id>/', views.edit_product, name='edit_product'),
]