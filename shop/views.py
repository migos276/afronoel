from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
import json
import urllib.parse

from .models import Category, Product, Brand, Promotion, Order, OrderItem


def home(request):
    """Page d'accueil"""
    categories = Category.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    bestsellers = Product.objects.filter(is_active=True, is_bestseller=True)[:12]
    flash_sales = Product.objects.filter(
        is_active=True, 
        is_flash_sale=True,
        flash_sale_end__gt=timezone.now()
    )[:6]
    brands = Brand.objects.filter(is_active=True)
    promotions = Promotion.objects.filter(is_active=True)[:3]
    
    # Produits par budget
    budget_under_20k = Product.objects.filter(is_active=True, price__lt=20000)[:4]
    budget_20_50k = Product.objects.filter(is_active=True, price__gte=20000, price__lt=50000)[:4]
    budget_50_100k = Product.objects.filter(is_active=True, price__gte=50000, price__lt=100000)[:4]
    budget_over_100k = Product.objects.filter(is_active=True, price__gte=100000)[:4]

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'bestsellers': bestsellers,
        'flash_sales': flash_sales,
        'brands': brands,
        'promotions': promotions,
        'budget_under_20k': budget_under_20k,
        'budget_20_50k': budget_20_50k,
        'budget_50_100k': budget_50_100k,
        'budget_over_100k': budget_over_100k,
    }
    return render(request, 'shop/home.html', context)


def category_view(request, slug):
    """Page catégorie"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Filtres
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'popular':
        products = products.order_by('-is_bestseller', '-created_at')
    else:
        products = products.order_by('-created_at')

    context = {
        'category': category,
        'products': products,
        'current_sort': sort,
    }
    return render(request, 'shop/category.html', context)


def product_view(request, slug):
    """Page produit"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'shop/product.html', context)


def search_view(request):
    """Recherche de produits"""
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'shop/search.html', context)


def cart_view(request):
    """Page panier"""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            subtotal = product.price * item['quantity']
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'size': item.get('size', ''),
                'color': item.get('color', ''),
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            pass
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'free_shipping': total >= settings.FREE_SHIPPING_THRESHOLD,
        'shipping_threshold': settings.FREE_SHIPPING_THRESHOLD,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
        'shop_name': settings.SHOP_NAME,
    }
    return render(request, 'shop/cart.html', context)


@require_POST
def add_to_cart(request):
    """Ajouter au panier (AJAX)"""
    data = json.loads(request.body)
    product_id = str(data.get('product_id'))
    quantity = int(data.get('quantity', 1))
    size = data.get('size', '')
    color = data.get('color', '')
    
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produit non trouvé'})
    
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        cart[product_id]['quantity'] += quantity
    else:
        cart[product_id] = {
            'quantity': quantity,
            'size': size,
            'color': color,
        }
    
    request.session['cart'] = cart
    request.session.modified = True
    
    cart_count = sum(item['quantity'] for item in cart.values())
    
    return JsonResponse({
        'success': True,
        'cart_count': cart_count,
        'message': f'{product.name} ajouté au panier'
    })


@require_POST
def update_cart(request):
    """Mettre à jour le panier (AJAX)"""
    data = json.loads(request.body)
    product_id = str(data.get('product_id'))
    quantity = int(data.get('quantity', 1))
    
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        if quantity > 0:
            cart[product_id]['quantity'] = quantity
        else:
            del cart[product_id]
    
    request.session['cart'] = cart
    request.session.modified = True
    
    # Recalculer le total
    total = 0
    for pid, item in cart.items():
        try:
            product = Product.objects.get(id=pid)
            total += product.price * item['quantity']
        except Product.DoesNotExist:
            pass
    
    cart_count = sum(item['quantity'] for item in cart.values())
    
    return JsonResponse({
        'success': True,
        'cart_count': cart_count,
        'total': total,
    })


@require_POST
def remove_from_cart(request):
    """Supprimer du panier (AJAX)"""
    data = json.loads(request.body)
    product_id = str(data.get('product_id'))
    
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        del cart[product_id]
    
    request.session['cart'] = cart
    request.session.modified = True
    
    cart_count = sum(item['quantity'] for item in cart.values())
    
    return JsonResponse({
        'success': True,
        'cart_count': cart_count,
    })


def generate_whatsapp_link(request):
    """Générer le lien WhatsApp avec le message pré-rempli"""
    cart = request.session.get('cart', {})
    if not cart:
        return JsonResponse({'success': False, 'error': 'Panier vide'})
    
    # Construire le message
    message_lines = [f"Bonjour {settings.SHOP_NAME} 🎄", "Je souhaite commander :", ""]
    total = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * item['quantity']
            total += subtotal
            
            line = f"• {product.name}"
            if item.get('size'):
                line += f" – Taille {item['size']}"
            if item.get('color'):
                line += f" – {item['color']}"
            line += f" – {item['quantity']}x – {product.price:,} FCFA".replace(",", " ")
            message_lines.append(line)
        except Product.DoesNotExist:
            pass
    
    message_lines.append("")
    message_lines.append(f"💰 Total : {total:,} FCFA".replace(",", " "))
    message_lines.append("")
    message_lines.append("📝 Mes informations :")
    message_lines.append("Nom : [à remplir]")
    message_lines.append("Téléphone : [à remplir]")
    message_lines.append("Ville : [Douala / Yaoundé / Abidjan / etc.]")
    message_lines.append("Adresse exacte de livraison : [à remplir]")
    message_lines.append("")
    message_lines.append("Merci et Joyeux Noël ! 🎅")
    
    message = "\n".join(message_lines)
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={encoded_message}"
    
    return JsonResponse({
        'success': True,
        'whatsapp_url': whatsapp_url,
        'message': message,
    })
