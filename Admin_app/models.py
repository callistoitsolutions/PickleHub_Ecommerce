from django.db import models

# Create your models here.


############# Admin Details Modal Starts Here #####################

class AdminDetails(models.Model):
    admin_name = models.CharField(max_length=200,blank=True,null=True)
    admin_email = models.CharField(max_length=200,blank=True,null=True)
    admin_phone = models.CharField(max_length=200,blank=True,null=True)
    admin_password = models.CharField(max_length=200,blank=True,null=True)
    

    def __str__(self):
        return f"{self.admin_email}-{self.admin_password}"
    

############### User Details Modal Starts Here ##############################

class UserDetails(models.Model):
    user_name = models.CharField(max_length=200,blank=True,null=True)
    user_email = models.CharField(max_length=200,blank=True,null=True)
    user_phone = models.CharField(max_length=200,blank=True,null=True)
    user_city = models.CharField(max_length=200,blank=True,null=True)
    user_password = models.CharField(max_length=200,blank=True,null=True)

    user_register_date = models.DateField(blank=True,null=True)
    user_register_time = models.TimeField(blank=True,null=True)
    

    def __str__(self):
        return f"{self.user_name}-{self.user_phone}"


############ Offer Banner Modal Starts Here ####################

class OfferBanner(models.Model):
    OFFER_TYPES = (
        ('main', 'Main Offer Banner'),
        ('potw', 'Pickle of the Week'),
    )

    # Core Shared Fields
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPES, default='main')
    name = models.CharField(max_length=200, help_text="Product name (e.g., Andhra Avakaya Mango Pickle)")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Sale price (₹)")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Original crossed-out price (₹)")
    url = models.CharField(max_length=255, blank=True, null=True, help_text="Relative URL or full link (e.g., /product/mango-pickle/)")
    
    #  Main Offer Specific Fields
    badge = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 🔥 LIMITED STOCK")
    description = models.CharField(max_length=255, blank=True, null=True, help_text="Short description for the main offer")
    discount_label = models.CharField(max_length=30, blank=True, null=True, help_text="e.g., 33% OFF")

    #  Pickle of the Week Specific Fields
    emoji = models.CharField(max_length=10, blank=True, null=True, default="", help_text="Emoji for the POTW banner")
    weight_type = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., 500g | Traditional Recipe")

    # Management Fields
    order = models.PositiveIntegerField(default=0, help_text="Controls the sequence they appear on the frontend")
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this banner from the frontend")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Offer Banner"
        verbose_name_plural = "Offer Banners"

    def __str__(self):
        return f"[{self.get_offer_type_display()}] {self.name}"

    def to_dict(self):
        """
        Helper method to easily serialize this model instance into the JSON 
        format your JavaScript expects for window.STATE.offers.
        """
        base_dict = {
            'id': self.id,
            'type': self.offer_type,
            'name': self.name,
            'price': str(self.price), # Convert Decimal to string for JS
            'oldPrice': str(self.old_price) if self.old_price else '',
            'url': self.url or '',
        }

        if self.offer_type == 'main':
            base_dict.update({
                'badge': self.badge or '',
                'desc': self.description or '',
                'discount': self.discount_label or '',
            })
        else:
            base_dict.update({
                'emoji': self.emoji or '',
                'weight': self.weight_type or '',
            })
            
        return base_dict
    
############## Offer Banner Modal Ends Here ############################


############# Brand Modal Starts Here #################################



from django.db import models
from django.utils.text import slugify


class Brand(models.Model):
    """
    Used for:
    - Product filter sidebar
    - Home page brand section
    """

    # Core Fields
    emoji = models.CharField(max_length=10, default='🏷️')
    name = models.CharField(max_length=200)
    
    # ✅ FIXED slug (important change)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    url = models.CharField(max_length=300, default='/', blank=True, null=True)

    # Extra Fields
    product_count = models.PositiveIntegerField(
        default=0,
        help_text='Shown as count badge in filter sidebar'
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text='Controls display order'
    )

    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.emoji} {self.name}"

    # ✅ AUTO GENERATE SLUG
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # Ensure unique slug
            while Brand.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'emoji': self.emoji,
            'name': self.name,
            'url': self.url or '',
            'slug': self.slug,
            'product_count': self.product_count
        }
############ Brand Modal Ends Here #################################


########### Review Modal Starts Here ############################

class Review(models.Model):
    avatar = models.CharField(max_length=10, default='', help_text="Emoji or short text")
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField(default=5, help_text="1 to 5 stars")
    text = models.TextField()
    
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Review by {self.name} ({self.rating} Stars)"

    def to_dict(self):
        return {
            'id': self.id,
            'avatar': self.avatar,
            'name': self.name,
            'city': self.city,
            'rating': self.rating,
            'text': self.text,
            'order': self.order
        }
    
################## Review Modal Ends Here ###############################


############ Newsletter Modal Starts Here ################################

class NewsletterSetting(models.Model):
    heading = models.CharField(max_length=200, default=" Get 15% OFF Your First Order!")
    description = models.TextField(default="Subscribe to receive exclusive deals, new pickle arrivals & Nagpur-only offers straight to your inbox.")
    placeholder = models.CharField(max_length=100, default="Enter your email address...")
    btn_text = models.CharField(max_length=50, default="Subscribe 🎉")
    privacy_note = models.CharField(max_length=200, default="No spam. Unsubscribe anytime. 🔒 Privacy protected.")
    url = models.CharField(max_length=500, default="/newsletter/subscribe/", blank=True)

    def __str__(self):
        return "Global Newsletter Settings"
    
############ Newsletter Modal Ends Here #################################

class HeroSection(models.Model):
    badge_text        = models.CharField(max_length=200, default="🏆 Nagpur's #1 Pickle Store")
    title_line1       = models.CharField(max_length=200, default="Discover")
    title_highlight   = models.CharField(max_length=200, default="Rare & Exclusive")
    title_line2       = models.CharField(max_length=200, default="Pickle Brands")
    subtitle          = models.TextField(
        default="Handpicked regional pickles from Andhra, Rajasthan, Punjab & more — "
                "not available in local stores. Order online with 24-hour delivery across Nagpur."
    )
    jar_emoji         = models.CharField(max_length=10, default="🫙")
    hero_image_url    = models.TextField(blank=True, default="")

    # Dynamic lists
    buttons_json      = models.JSONField(default=list)   # [{icon, text, url, type}, ...]
    stats_json        = models.JSONField(default=list)   # [{num, lbl}, ...]
    float_badges_json = models.JSONField(default=list)   # ["🌶️ Extra Spicy", ...]

    is_visible        = models.BooleanField(default=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Hero Section"
        verbose_name_plural = "Hero Section"

    def __str__(self):
        return f"Hero Section (updated {self.updated_at.strftime('%d %b %Y %H:%M')})"

    @classmethod
    def get_or_create_default(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create(
                buttons_json=[
                    {"icon": "fa-shopping-bag", "text": "Shop Now",          "url": "/products/",                 "type": "primary"},
                    {"icon": "fa-whatsapp",     "text": "Order on WhatsApp", "url": "https://wa.me/919876543210", "type": "secondary"},
                ],
                stats_json=[
                    {"num": "50+",   "lbl": "Pickle Brands"},
                    {"num": "200+",  "lbl": "Products"},
                    {"num": "5000+", "lbl": "Happy Customers"},
                    {"num": "24Hr",  "lbl": "Delivery"},
                ],
                float_badges_json=["🌶️ Extra Spicy", "✅ 100% Natural", "🚚 Free Delivery"],
            )
        return obj


# ══════════════════════════════════════════════════════
# 2. FEATURES SECTION  (NEW)
# ══════════════════════════════════════════════════════
class FeaturesSection(models.Model):
    """
    Stores the Features Strip section shown below the hero.
    items_json holds the list of feature cards — each card has:
        {
            "ico":   "🚚",
            "title": "Free Delivery",
            "sub":   "Orders above ₹499"
        }
    Admin can add / edit / remove / reorder these from the builder.
    """
    # Dynamic list of feature cards
    items_json = models.JSONField(
        default=list,
        help_text='List of feature cards: [{"ico":"🚚","title":"Free Delivery","sub":"Orders above ₹499"}, ...]'
    )

    is_visible = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Features Section"
        verbose_name_plural = "Features Section"

    def __str__(self):
        return f"Features Section (updated {self.updated_at.strftime('%d %b %Y %H:%M')})"

    @classmethod
    def get_or_create_default(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create(
                items_json=[
                    {"ico": "🚚", "title": "Free Delivery",  "sub": "Orders above ₹499"},
                    {"ico": "🌿", "title": "100% Natural",   "sub": "No preservatives"},
                    {"ico": "🔄", "title": "Easy Returns",   "sub": "7-day return policy"},
                    {"ico": "🔒", "title": "Secure Payment", "sub": "UPI / Razorpay / COD"},
                ]
            )
        return obj



class CategorySection(models.Model):
    """
    Stores the 'Shop by Category' section shown on the home page.

    section_title   — heading shown above the grid
    section_subtitle— subheading shown below the title
    items_json      — list of category cards, each card:
        {
            "emoji":       "🥭",
            "name":        "Mango Pickle",
            "count":       "32 products",
            "url":         "/category/mango/",
            "bg_gradient": "linear-gradient(135deg, #fff3e0, #ffcc80)"
        }
    is_visible      — show/hide the whole section on the home page
    """

    section_title    = models.CharField(max_length=200, default="Shop by Category")
    section_subtitle = models.CharField(
        max_length=300,
        default="Browse our wide range of authentic pickle varieties"
    )
    items_json = models.JSONField(
        default=list,
        help_text='List of category cards: [{"emoji":"🥭","name":"Mango Pickle","count":"32 products","url":"/category/mango/","bg_gradient":"linear-gradient(135deg,#fff3e0,#ffcc80)"}, ...]'
    )
    is_visible = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Category Section"
        verbose_name_plural = "Category Section"

    def __str__(self):
        return f"Category Section (updated {self.updated_at.strftime('%d %b %Y %H:%M')})"

    @classmethod
    def get_or_create_default(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create(
                items_json=[
                    {"emoji": "🥭", "name": "Mango Pickle",      "count": "32 products", "url": "/category/mango/",    "bg_gradient": "linear-gradient(135deg,#fff3e0,#ffcc80)"},
                    {"emoji": "🧄", "name": "Garlic Pickle",     "count": "18 products", "url": "/category/garlic/",   "bg_gradient": "linear-gradient(135deg,#fce4ec,#f8bbd9)"},
                    {"emoji": "🍋", "name": "Lemon Pickle",      "count": "24 products", "url": "/category/lemon/",    "bg_gradient": "linear-gradient(135deg,#f9fbe7,#f0f4c3)"},
                    {"emoji": "🌶️","name": "Chilli Pickle",     "count": "15 products", "url": "/category/chilli/",   "bg_gradient": "linear-gradient(135deg,#fce4ec,#ffcdd2)"},
                    {"emoji": "🫙", "name": "Mixed Pickle",      "count": "20 products", "url": "/category/mixed/",    "bg_gradient": "linear-gradient(135deg,#e8f5e9,#c8e6c9)"},
                    {"emoji": "🗺️","name": "Regional Specials", "count": "40 products", "url": "/category/regional/", "bg_gradient": "linear-gradient(135deg,#e3f2fd,#bbdefb)"},
                ]
            )
        return obj
    
    
    
    
    
############ Pincode Manager  Modals Start Here ############################################################





class DeliveryPincode(models.Model):
    """Stores every pincode PickleHub delivers to."""

    pincode      = models.CharField(max_length=10, unique=True)
    area_name    = models.CharField(max_length=120)          # e.g. "Dharampeth"
    city         = models.CharField(max_length=80, default="Nagpur")
    state        = models.CharField(max_length=80, default="Maharashtra")

    is_active    = models.BooleanField(default=True)         # toggle delivery on/off
    cod_allowed  = models.BooleanField(default=True)         # Cash-on-delivery flag
    delivery_days = models.PositiveSmallIntegerField(default=2)  # estimated days

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['pincode']
        verbose_name        = "Delivery Pincode"
        verbose_name_plural = "Delivery Pincodes"

    def __str__(self):
        return f"{self.pincode} – {self.area_name} ({self.city})"




class DemandReport(models.Model):
    """
    Customers request products / pincodes not yet available.
    Admins use this to decide what to stock or where to expand.
    """

    TYPE_CHOICES = [
        ('product',  'Product Demand'),
        ('pincode',  'Pincode Demand'),
        ('category', 'Category Demand'),
    ]

    STATUS_CHOICES = [
        ('new',         'New'),
        ('reviewed',    'Reviewed'),
        ('in_progress', 'In Progress'),
        ('fulfilled',   'Fulfilled'),
        ('rejected',    'Rejected'),
    ]

    demand_type      = models.CharField(max_length=20, choices=TYPE_CHOICES)
    customer_name    = models.CharField(max_length=120, blank=True)
    customer_phone   = models.CharField(max_length=15,  blank=True)
    customer_email   = models.EmailField(blank=True)

    # What they want
    product_name     = models.CharField(max_length=200, blank=True,
                                        help_text="Fill if demand_type = product")
    requested_pincode = models.CharField(max_length=10, blank=True,
                                         help_text="Fill if demand_type = pincode")
    category_name    = models.CharField(max_length=120, blank=True,
                                        help_text="Fill if demand_type = category")
    notes            = models.TextField(blank=True)

    # Admin fields
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                        default='new')
    admin_remarks    = models.TextField(blank=True)
    vote_count       = models.PositiveIntegerField(default=1,
                          help_text="How many customers want the same thing")

    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-vote_count', '-created_at']
        verbose_name        = "Demand Report"
        verbose_name_plural = "Demand Reports"

    def __str__(self):
        label = self.product_name or self.requested_pincode or self.category_name
        return f"[{self.get_demand_type_display()}] {label} (votes: {self.vote_count})"






############ Pincode Manager  Modals Start Here ############################################################