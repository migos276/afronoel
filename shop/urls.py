from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('categorie/<slug:slug>/', views.category_view, name='category'),
    path('produit/<slug:slug>/', views.product_view, name='product'),
    path('recherche/', views.search_view, name='search'),
    path('panier/', views.cart_view, name='cart'),
    path('api/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/update/', views.update_cart, name='update_cart'),
    path('api/cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('api/whatsapp-link/', views.generate_whatsapp_link, name='whatsapp_link'),
]
