from .models import Category

def cart_context(request):
    """Contexte du panier pour tous les templates"""
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    return {
        'cart_count': cart_count,
    }

def categories_context(request):
    """Catégories pour le menu"""
    return {
        'nav_categories': Category.objects.filter(is_active=True)[:6],
    }
