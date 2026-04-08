from django.db import models





############ Product Module Modal Starts Here ####################

class Product(models.Model):
    """
    Individual pickle product shown on the products listing page.
    Links to Brand and Category (FK).
    """

    BADGE_CHOICES = [
        ('Bestseller',    'Bestseller'),
        ('New Arrival',   'New Arrival'),
        ('Premium',       'Premium'),
        ('Hot 🔥',        'Hot 🔥'),
        ('Organic',       'Organic'),
        ('Limited',       'Limited'),
        ('Rare Find',     'Rare Find'),
        ('Nagpur Special','Nagpur Special'),
        ('',              'No Badge'),
    ]

    # ── identity ──
    emoji        = models.CharField(max_length=10, default='🫙')
    image        = models.ImageField(upload_to='products/', null=True, blank=True)
    name         = models.CharField(max_length=300)
    slug         = models.SlugField(max_length=300, unique=True)

    # ── relations ──
    brand        = models.ForeignKey(
                       'Admin_app.Brand',
                       on_delete=models.SET_NULL,
                       null=True, blank=True,
                       related_name='products'
                   )
    category     = models.ForeignKey(
                       'Admin_app.CategorySection',
                       on_delete=models.SET_NULL,
                       null=True, blank=True,
                       related_name='products',
                       help_text='Links to CategorySection for filter sidebar'
                   )

    # ── display details ──
    weight       = models.CharField(max_length=100, default='500g')
    oil_type     = models.CharField(max_length=100, default='Mustard Oil')
    region       = models.CharField(max_length=200, blank=True, default='',
                       help_text='e.g. Andhra Pradesh, Rajasthan')
    badge        = models.CharField(max_length=50, choices=BADGE_CHOICES, blank=True, default='')
    badge_color  = models.CharField(max_length=200,
                       default='linear-gradient(135deg,#e85d04,#f48c06)',
                       help_text='CSS gradient for the badge background')
    card_bg      = models.CharField(max_length=200,
                       default='linear-gradient(135deg,#fff3e0,#ffcc80)',
                       help_text='CSS gradient for product card background')

    # ── pricing ──
    price        = models.PositiveIntegerField(default=0, help_text='Sale price in ₹')
    old_price    = models.PositiveIntegerField(default=0, help_text='Original price in ₹')
    discount     = models.CharField(max_length=20, blank=True, default='',
                       help_text='e.g. 29% off — auto-calculated if left blank')
    
    
    
    
    
    # ── descriptions ──
    short_description = models.CharField(
    max_length=200, blank=True, default='',
    help_text='Shown on product card in listing page'
    )
    long_description  = models.TextField(
    blank=True, default='',
    help_text='Full detail shown on product page (HTML allowed)'
    )
    highlights        = models.JSONField(
    default=list, blank=True,
    help_text='List of bullet-point highlights shown on product page'
    )

# ── extra identity ──
    sku               = models.CharField(max_length=100, blank=True, default='')
    hsn_code          = models.CharField(max_length=20, blank=True, default='',
                        help_text='HSN code for GST')
    unit_type         = models.CharField(max_length=50, blank=True, default='grams',
                        help_text='grams / kg / ml / ltr / piece / pack')

# ── pricing extras ──
    cost_price        = models.PositiveIntegerField(
                        default=0, help_text='Internal cost price — not shown to customers'
                    )
    gst_rate          = models.PositiveIntegerField(
                        default=5, help_text='GST % rate e.g. 0, 5, 12, 18, 28'
                    )
    gst_inclusive     = models.BooleanField(
                        default=True, help_text='Is selling price inclusive of GST?'
                    )
    free_delivery     = models.CharField(
                        max_length=20, default='site_rule',
                        choices=[
                            ('site_rule', 'Follow site rule'),
                            ('always',    'Always free'),
                            ('never',     'Never free'),
                        ]
                    )

# ── stock extras ──
    shelf_life        = models.CharField(max_length=100, blank=True, default='',
                        help_text='e.g. 12 months')
    storage_info      = models.CharField(max_length=200, blank=True, default='',
                        help_text='e.g. Cool & dry place')
    min_order_qty     = models.PositiveIntegerField(default=1)
    max_order_qty     = models.PositiveIntegerField(default=5)

# ── seo ──
    seo_title         = models.CharField(max_length=60, blank=True, default='')
    seo_description   = models.CharField(max_length=160, blank=True, default='')
    seo_keywords      = models.CharField(max_length=500, blank=True, default='',
                        help_text='Comma separated keywords')
    tags              = models.JSONField(default=list, blank=True)

# ── coupon assignment ──
    assigned_coupons  = models.ManyToManyField(
                        'Coupon',
                        blank=True,
                        related_name='products',
                        help_text='Coupons directly assigned to this product'
                    )

    # ── stock ──
    stock                  = models.PositiveIntegerField(
                                 default=100,
                                 help_text='Current stock quantity. Set to 0 to auto mark as Out of Stock.'
                             )
    low_stock_threshold    = models.PositiveIntegerField(
                                 default=20,
                                 help_text='Show low-stock warning when stock falls below this number.'
                             )
    low_stock_label        = models.CharField(
                                 max_length=100, blank=True, default='',
                                 help_text='e.g. "🔥 Only 12 left" — leave blank to auto-generate'
                             )
    is_out_of_stock_manual = models.BooleanField(
                                 default=False,
                                 help_text=(
                                     'Force this product to show as Out of Stock '
                                     'regardless of the actual stock number. '
                                     'Use this when stock is unavailable due to supplier delay, '
                                     'seasonal unavailability, etc.'
                                 )
                             )

    # ── social proof ──
    rating       = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    review_count = models.PositiveIntegerField(default=0)

    # ── whatsapp ──
    whatsapp_number = models.CharField(
                          max_length=20, default='919876543210',
                          help_text='Without + sign e.g. 919876543210'
                      )

    # ── flags ──
    is_active    = models.BooleanField(default=True)
    is_featured  = models.BooleanField(
                       default=False,
                       help_text='Show in Best Sellers / homepage featured grid'
                   )
    sort_order   = models.PositiveIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Product'
        verbose_name_plural = 'Products'
        ordering            = ['sort_order', '-created_at']

    def __str__(self):
        return f'{self.emoji} {self.name}'

    # ──────────────────────────────────────────
    #  STOCK & AVAILABILITY PROPERTIES
    # ──────────────────────────────────────────

    @property
    def is_out_of_stock(self):
        """
        Returns True if the product should be shown as Out of Stock.
        Two ways this can happen:
          1. Admin manually toggled is_out_of_stock_manual = True
          2. stock has reached 0 automatically
        """
        return self.is_out_of_stock_manual or self.stock == 0

    @property
    def is_low_stock(self):
        """
        Returns True when stock is low but NOT zero.
        Low stock warning is NOT shown when product is fully out of stock.
        """
        return (not self.is_out_of_stock) and (self.stock <= self.low_stock_threshold)

    @property
    def stock_status(self):
        """
        Returns one of three string values — used in stock manager template
        to drive badge colours.
          'out_of_stock' → red
          'low_stock'    → yellow
          'in_stock'     → green
        """
        if self.is_out_of_stock:
            return 'out_of_stock'
        if self.is_low_stock:
            return 'low_stock'
        return 'in_stock'

    @property
    def low_stock_text(self):
        """
        Returns the low-stock label shown on the product card.
        Priority:
          1. Use custom label if admin has set one.
          2. Auto-generate "🔥 Only X left" when stock is low.
          3. Return empty string when fully out of stock or stock is fine.
        """
        if self.is_out_of_stock:
            return ''                          # OOS ribbon handles this case
        if self.low_stock_label:
            return self.low_stock_label
        if self.is_low_stock:
            return f'🔥 Only {self.stock} left'
        return ''

    # ──────────────────────────────────────────
    #  PRICING PROPERTIES
    # ──────────────────────────────────────────

    @property
    def discount_pct(self):
        """Auto-calculate discount % from price / old_price."""
        if self.old_price and self.old_price > self.price:
            return int(round((self.old_price - self.price) / self.old_price * 100))
        return 0

    @property
    def discount_label(self):
        """
        Returns the discount label shown on the card.
        Uses manual override if set, otherwise auto-calculates.
        """
        return self.discount or (f'{self.discount_pct}% off' if self.discount_pct else '')

    # ──────────────────────────────────────────
    #  DISPLAY PROPERTIES
    # ──────────────────────────────────────────

    @property
    def stars_html(self):
        """Returns star characters e.g. ★★★★½☆ for rating 4.5"""
        full  = int(self.rating)
        half  = 1 if (self.rating - full) >= 0.5 else 0
        empty = 5 - full - half
        return '★' * full + ('½' if half else '') + '☆' * empty

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('product_details', kwargs={'slug': self.slug})
# ══════════════════════════════════════════════════════
# 6. PRODUCT PAGE SETTINGS  (filter sidebar config)
# ══════════════════════════════════════════════════════
class ProductPageSettings(models.Model):
    """
    Controls which filter sections are visible on the products listing page
    and their configuration.  Singleton — always use get_or_create_default().
    """
    # ── filter visibility toggles ──
    show_category_filter = models.BooleanField(default=True)
    show_brand_filter    = models.BooleanField(default=True)
    show_price_filter    = models.BooleanField(default=True)
    show_region_filter   = models.BooleanField(default=True)
    show_rating_filter   = models.BooleanField(default=True)
    show_weight_filter   = models.BooleanField(default=True)

    # ── price range config ──
    price_min = models.PositiveIntegerField(default=50)
    price_max = models.PositiveIntegerField(default=800)

    # ── region options (JSON list of {name, count}) ──
    regions_json = models.JSONField(
        default=list,
        help_text='[{"name":"Andhra Pradesh","count":35}, ...]'
    )

    # ── weight options (JSON list of {label}) ──
    weights_json = models.JSONField(
        default=list,
        help_text='[{"label":"100g - 200g"}, ...]'
    )

    # ── page meta ──
    page_title    = models.CharField(max_length=200,
                        default='All Pickles - Shop by Brand, Category & Region | PickleHub Nagpur')
    whatsapp_number = models.CharField(max_length=20, default='919876543210')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Product Page Settings'
        verbose_name_plural = 'Product Page Settings'

    def __str__(self):
        return f'Product Page Settings (updated {self.updated_at.strftime("%d %b %Y %H:%M")})'

    @classmethod
    def get_or_create_default(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create(
                regions_json=[
                    {'name': 'Andhra Pradesh', 'count': 35},
                    {'name': 'Rajasthan',       'count': 28},
                    {'name': 'Punjab',          'count': 16},
                    {'name': 'Gujarat',         'count': 19},
                    {'name': 'Kerala',          'count': 14},
                ],
                weights_json=[
                    {'label': '100g - 200g'},
                    {'label': '250g - 500g'},
                    {'label': '500g - 1kg'},
                    {'label': '1kg+'},
                ],
            )
        return obj


############ End Product Module Modal Here ####################


############ Deals & Offers Modal Starts Here ###############################################
class DealOfTheDay(models.Model):
    product      = models.ForeignKey(
                       'products.Product',
                       on_delete=models.SET_NULL,
                       null=True, blank=True,
                       related_name='deal_of_the_day'
                   )
    badge_text   = models.CharField(max_length=50, default="🔥 Deal of the Day")
    end_time     = models.DateTimeField(null=True, blank=True)
    float_badge1 = models.CharField(max_length=60, default="⭐ 4.8 • 320 reviews")
    float_badge2 = models.CharField(max_length=60, default="✅ 100% Natural")
    is_visible   = models.BooleanField(default=True)

    # ── These pull from Product automatically ──
    @property
    def title(self):
        return self.product.name if self.product else ""

    @property
    def subtitle(self):
        return self.product.region or self.product.weight if self.product else ""

    @property
    def emoji(self):
        return self.product.emoji if self.product else "🥒"

    @property
    def price(self):
        return self.product.price if self.product else 0

    @property
    def old_price(self):
        return self.product.old_price if self.product else 0

    @property
    def url(self):
        return self.product.get_absolute_url() if self.product else "#"

    @property
    def discount_pct(self):
        return self.product.discount_pct if self.product else 0

    class Meta:
        verbose_name = "Deal of the Day"

    def __str__(self):
        return f"Deal → {self.product.name}" if self.product else "Deal of the Day"



class Coupon(models.Model):
    TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('flat', 'Flat Discount'),
        ('free_del', 'Free Delivery'),
        ('bogo', 'Buy 1 Get 1'),
        ('coupon', 'Coupon Code'),
    ]
    
    # --- Advanced Fields (Used by your new Admin UI) ---
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100, default="Promo Offer") 
    description = models.TextField(blank=True, null=True)
    coupon_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='percent')
    
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    uses = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(default=1)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    applies_to = models.CharField(max_length=50, default='all')
    
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    first_order_only = models.BooleanField(default=False)

    # --- Old Fields (Kept safely so you don't lose data) ---
    icon = models.CharField(max_length=10, default="🎁", blank=True)
    # FIX: Added default="" to prevent the migration crash!
    discount_val = models.CharField(max_length=50, default="", blank=True, help_text="e.g. Buy 1 Get 1 or ₹100 OFF")
    expiry_note = models.CharField(max_length=100, default="Valid till 30 Apr 2026", blank=True)
    color_bg = models.CharField(max_length=30, default="#e4eeff", blank=True)
    show_on_strip = models.BooleanField(default=False)
    show_on_wall = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = "Coupon / Offer"

    def __str__(self):
        return f"{self.code} — {self.name}"

# ── MODEL 3: Today's Offer Products ─────────────────────────────



class TodaysOffer(models.Model):
    """
    Today's Offer — links to an existing Product via FK.
    Does NOT store name, price, brand, emoji etc.
    All product data comes from the linked Product model.
    Only stores: which product, what badge, is it visible.
    """

    BADGE_CHOICES = [
        ('deal', 'Deal'),
        ('hot',  'Hot'),
        ('new',  'New'),
        ('bogo', 'BOGO'),
        ('disc', 'Discount'),
    ]

    # ── MAIN LINK (most important field) ──
    # ── MAIN LINK (most important field) ──
    product = models.ForeignKey(
    'products.Product',
    on_delete=models.CASCADE,
    related_name='todays_offers',
    null=True,      # ✅ add this
    blank=True,     # ✅ add this
    )
    # ── offer badge (only thing specific to the offer) ──
    badge       = models.CharField(max_length=10, choices=BADGE_CHOICES, default='deal')
    badge_label = models.CharField(max_length=20, default='DEAL',
                      help_text='Text shown on badge e.g. HOT DEAL, BOGO, 30% OFF')

    # ── visibility ──
    is_visible = models.BooleanField(
        default=True,
        help_text='Uncheck to hide this offer from the website without deleting it'
    )

    # ── ordering ──
    order = models.PositiveIntegerField(
        default=0,
        help_text='Lower number = shown first. Use to control display order.'
    )

    class Meta:
        ordering            = ['order', 'id']
        verbose_name        = "Today's Offer"
        verbose_name_plural = "Today's Offers"

    def __str__(self):
        return f"{self.badge_label} — {self.product.name}"

    # ── helper properties (so templates can do item.name instead of item.product.name) ──
    @property
    def name(self):
        return self.product.name

    @property
    def emoji(self):
        return self.product.emoji

    @property
    def price(self):
        return self.product.price

    @property
    def old_price(self):
        return self.product.old_price

    @property
    def brand(self):
        return self.product.brand

    @property
    def weight(self):
        return self.product.weight

    @property
    def whatsapp_number(self):
        return self.product.whatsapp_number

# ── MODEL 4: Ticker Messages ─────────────────────────────────────
class TickerMessage(models.Model):
    text      = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    order     = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Ticker Message"

    def __str__(self):
        return self.text
    
    
############ Deals & Offers Modal Ends Here ###############################################





class Wishlist(models.Model):
    user       = models.ForeignKey('Admin_app.UserDetails', on_delete=models.CASCADE, related_name='wishlist_items')
    product    = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='wishlisted_by')
    added_on   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')   # one entry per user+product
        ordering        = ['-added_on']

    def __str__(self):
        return f"{self.user} → {self.product}"