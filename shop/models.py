from django.db import models
from django.urls import reverse
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Classe Font Awesome")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:category', kwargs={'slug': self.slug})


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Description")
    price = models.PositiveIntegerField(verbose_name="Prix (FCFA)")
    old_price = models.PositiveIntegerField(blank=True, null=True, verbose_name="Ancien prix")
    image = models.ImageField(upload_to='products/')
    image_2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='products/', blank=True, null=True)
    image_4 = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    sizes = models.CharField(max_length=200, blank=True, help_text="Tailles séparées par des virgules: S, M, L, XL")
    colors = models.CharField(max_length=200, blank=True, help_text="Couleurs séparées par des virgules")
    is_featured = models.BooleanField(default=False, verbose_name="Produit vedette")
    is_bestseller = models.BooleanField(default=False, verbose_name="Best-seller")
    is_flash_sale = models.BooleanField(default=False, verbose_name="Vente flash")
    flash_sale_end = models.DateTimeField(blank=True, null=True, verbose_name="Fin vente flash")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product', kwargs={'slug': self.slug})

    @property
    def discount_percentage(self):
        if self.old_price and self.old_price > self.price:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return 0

    @property
    def sizes_list(self):
        if self.sizes:
            return [s.strip() for s in self.sizes.split(',')]
        return []

    @property
    def colors_list(self):
        if self.colors:
            return [c.strip() for c in self.colors.split(',')]
        return []

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def flash_sale_active(self):
        if self.is_flash_sale and self.flash_sale_end:
            return timezone.now() < self.flash_sale_end
        return False


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    customer_name = models.CharField(max_length=100, verbose_name="Nom du client")
    customer_phone = models.CharField(max_length=20, verbose_name="Téléphone")
    customer_city = models.CharField(max_length=100, verbose_name="Ville")
    customer_address = models.TextField(verbose_name="Adresse de livraison")
    total_amount = models.PositiveIntegerField(verbose_name="Montant total (FCFA)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_num = int(last_order.order_number.replace('CMD', ''))
                self.order_number = f"CMD{last_num + 1:06d}"
            else:
                self.order_number = "CMD000001"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Article commandé"
        verbose_name_plural = "Articles commandés"

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    @property
    def subtotal(self):
        return self.price * self.quantity


class Promotion(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='promotions/')
    link = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"
        ordering = ['order']

    def __str__(self):
        return self.title


class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brands/')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Marque"
        verbose_name_plural = "Marques"
        ordering = ['order']

    def __str__(self):
        return self.name
