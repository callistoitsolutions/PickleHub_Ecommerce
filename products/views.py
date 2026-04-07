from django.shortcuts import render
import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.core.paginator import Paginator
from django.utils.text import slugify
from products.models import *
from Admin_app.models import *
from products.product_utils  import _product_page_data








# ── SAVE BRAND (AJAX POST) ────────────────────────────────────────────────────
@require_POST
def save_brand(request):
    """
    Creates or updates brands from the builder.

    Expected body:
    {
        "brands": [
            {
                "id":            1,         // null for new
                "emoji":         "🏜️",
                "name":          "Rajasthani Pickles",
                "url":           "/brand/rajasthani-pickles/",
                "product_count": 28,
                "is_active":     true,
                "sort_order":    0
            },
            ...
        ]
    }
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    brands_payload = data.get('brands', [])
    saved_ids = []

    for b in brands_payload:
        bid = b.get('id')
        name = b.get('name', '').strip()
        if not name:
            continue
        brand_slug = slugify(name)

        if bid:
            # update existing
            try:
                obj = Brand.objects.get(id=bid)
                obj.emoji         = b.get('emoji',         obj.emoji)
                obj.name          = name
                obj.slug          = brand_slug
                obj.url           = b.get('url',           obj.url)
                obj.product_count = b.get('product_count', obj.product_count)
                obj.is_active     = b.get('is_active',     obj.is_active)
                obj.sort_order    = b.get('sort_order',    obj.sort_order)
                obj.save()
                saved_ids.append(obj.id)
            except Brand.DoesNotExist:
                pass
        else:
            # create new — handle duplicate slugs
            counter = 1
            original_slug = brand_slug
            while Brand.objects.filter(slug=brand_slug).exists():
                brand_slug = f'{original_slug}-{counter}'
                counter += 1
            obj = Brand.objects.create(
                emoji         = b.get('emoji',         '🏷️'),
                name          = name,
                slug          = brand_slug,
                url           = b.get('url',           f'/brand/{brand_slug}/'),
                product_count = b.get('product_count', 0),
                is_active     = b.get('is_active',     True),
                sort_order    = b.get('sort_order',    0),
            )
            saved_ids.append(obj.id)

    return JsonResponse({'ok': True, 'message': f'✅ {len(saved_ids)} brand(s) saved!', 'saved_ids': saved_ids})


# ── DELETE BRAND (AJAX POST) ──────────────────────────────────────────────────
@require_POST
def delete_brand(request, brand_id):
    try:
        Brand.objects.filter(id=brand_id).delete()
        return JsonResponse({'ok': True, 'message': '🗑️ Brand deleted'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ── LOAD ALL BRANDS (AJAX GET) ────────────────────────────────────────────────
def load_brands(request):
    brands = Brand.objects.filter(is_active=True).order_by('sort_order', 'name')
    return JsonResponse({
        'ok': True,
        'brands': [
            {
                'id':            b.id,
                'emoji':         b.emoji,
                'name':          b.name,
                'slug':          b.slug,
                'url':           b.url,
                'product_count': b.product_count,
                'is_active':     b.is_active,
                'sort_order':    b.sort_order,
            }
            for b in brands
        ]
    })




############################## Products Views Section Starts Here ###############################################


@require_POST
def save_product(request):
    try:
        if request.content_type and 'multipart' in request.content_type:
            data   = request.POST
            raw_id = data.get('id', '').strip()
            pid    = int(raw_id) if raw_id else None
            name   = data.get('name', '').strip()
        else:
            data = json.loads(request.body)
            pid  = data.get('id')
            name = data.get('name', '').strip()

        product_slug = slugify(name)
        brand_id     = data.get('brand_id')
        category_id  = data.get('category_id')
        brand_obj    = Brand.objects.filter(id=brand_id).first()        if brand_id    else None
        category_obj = CategorySection.objects.filter(id=category_id).first() if category_id else None

        if pid:
            try:
                p = Product.objects.get(id=pid)
            except Product.DoesNotExist:
                return JsonResponse({'ok': False, 'error': 'Product not found'}, status=404)
        else:
            p = Product()
            counter, original_slug = 1, product_slug
            while Product.objects.filter(slug=product_slug).exists():
                product_slug = f'{original_slug}-{counter}'; counter += 1
            p.slug = product_slug

        # ── existing fields ──
        p.emoji           = data.get('emoji',            p.emoji if pid else '🫙')
        p.name            = name
        p.brand           = brand_obj
        p.category        = category_obj
        p.weight          = data.get('weight',           getattr(p, 'weight',          '500g'))
        p.oil_type        = data.get('oil_type',         getattr(p, 'oil_type',        'Mustard Oil'))
        p.region          = data.get('region',           getattr(p, 'region',          ''))
        p.badge           = data.get('badge',            getattr(p, 'badge',           ''))
        p.badge_color     = data.get('badge_color',      getattr(p, 'badge_color',     'linear-gradient(135deg,#e85d04,#f48c06)'))
        p.card_bg         = data.get('card_bg',          getattr(p, 'card_bg',         'linear-gradient(135deg,#fff3e0,#ffcc80)'))
        p.price           = int(data.get('price',        getattr(p, 'price',           0))   or 0)
        p.old_price       = int(data.get('old_price',    getattr(p, 'old_price',       0))   or 0)
        p.discount        = data.get('discount',         getattr(p, 'discount',        ''))
        p.stock           = int(data.get('stock',        getattr(p, 'stock',           100)) or 100)
        p.low_stock_label = data.get('low_stock_label',  getattr(p, 'low_stock_label', ''))
        p.rating          = float(data.get('rating',     getattr(p, 'rating',          4.5)) or 4.5)
        p.review_count    = int(data.get('review_count', getattr(p, 'review_count',    0))   or 0)
        p.whatsapp_number = data.get('whatsapp_number',  getattr(p, 'whatsapp_number', '919876543210'))
        p.is_active       = str(data.get('is_active',    getattr(p, 'is_active',       True))).lower()  not in ('false', '0', 'no')
        p.is_featured     = str(data.get('is_featured',  getattr(p, 'is_featured',     False))).lower() not in ('false', '0', 'no')
        p.sort_order      = int(data.get('sort_order',   getattr(p, 'sort_order',      0))   or 0)

        # ✅ new fields
        p.short_description = data.get('short_description', getattr(p, 'short_description', ''))
        p.long_description  = data.get('long_description',  getattr(p, 'long_description',  ''))
        p.sku               = data.get('sku',               getattr(p, 'sku',               ''))
        p.hsn_code          = data.get('hsn_code',          getattr(p, 'hsn_code',          ''))
        p.unit_type         = data.get('unit_type',         getattr(p, 'unit_type',         'grams'))
        p.cost_price        = int(data.get('cost_price',    getattr(p, 'cost_price',        0))   or 0)
        p.gst_rate          = int(data.get('gst_rate',      getattr(p, 'gst_rate',          5))   or 5)
        p.gst_inclusive     = str(data.get('gst_inclusive', getattr(p, 'gst_inclusive',     True))).lower() not in ('false', '0', 'no')
        p.free_delivery     = data.get('free_delivery',     getattr(p, 'free_delivery',     'site_rule'))
        p.shelf_life        = data.get('shelf_life',        getattr(p, 'shelf_life',        ''))
        p.storage_info      = data.get('storage_info',      getattr(p, 'storage_info',      ''))
        p.min_order_qty     = int(data.get('min_order_qty', getattr(p, 'min_order_qty',     1))   or 1)
        p.max_order_qty     = int(data.get('max_order_qty', getattr(p, 'max_order_qty',     5))   or 5)
        p.seo_title         = data.get('seo_title',         getattr(p, 'seo_title',         ''))
        p.seo_description   = data.get('seo_description',   getattr(p, 'seo_description',   ''))
        p.seo_keywords      = data.get('seo_keywords',      getattr(p, 'seo_keywords',      ''))

        # highlights and tags are JSON arrays sent as JSON strings
        import json as _json
        raw_highlights = data.get('highlights', '')
        raw_tags       = data.get('tags', '')
        try:
            p.highlights = _json.loads(raw_highlights) if raw_highlights else getattr(p, 'highlights', [])
        except Exception:
            p.highlights = []
        try:
            p.tags = _json.loads(raw_tags) if raw_tags else getattr(p, 'tags', [])
        except Exception:
            p.tags = []

        if 'image' in request.FILES:
            p.image = request.FILES['image']

        p.save()

        # ✅ save assigned coupons (M2M) — ids sent as JSON array string
        raw_coupons = data.get('assigned_coupon_ids', '[]')
        try:
            coupon_ids = _json.loads(raw_coupons) if isinstance(raw_coupons, str) else raw_coupons
            p.assigned_coupons.set(coupon_ids)
        except Exception:
            pass

        return JsonResponse({
            'ok':        True,
            'message':   '✅ Product saved!',
            'id':        p.id,
            'slug':      p.slug,
            'image_url': p.image.url if p.image else '',
        })

    except Exception as e:
        import traceback
        return JsonResponse({
            'ok': False, 'error': str(e), 'traceback': traceback.format_exc()
        }, status=400)
        
        
# ── DELETE PRODUCT (AJAX POST) ────────────────────────────────────────────────
@require_POST
def delete_product(request, product_id):
    try:
        Product.objects.filter(id=product_id).delete()
        return JsonResponse({'ok': True, 'message': '🗑️ Product deleted'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ── SAVE FILTER SETTINGS (AJAX POST) ─────────────────────────────────────────
@require_POST
def save_product_filter_settings(request):
    """
    Saves ProductPageSettings from filter builder.

    Expected body:
    {
        "show_category_filter": true,
        "show_brand_filter":    true,
        "show_price_filter":    true,
        "show_region_filter":   true,
        "show_rating_filter":   true,
        "show_weight_filter":   true,
        "price_min":            50,
        "price_max":            800,
        "regions_json": [{"name":"Andhra Pradesh","count":35}, ...],
        "weights_json": [{"label":"100g - 200g"}, ...],
        "page_title":           "All Pickles | PickleHub",
        "whatsapp_number":      "919876543210"
    }
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    s = ProductPageSettings.get_or_create_default()
    s.show_category_filter = data.get('show_category_filter', s.show_category_filter)
    s.show_brand_filter    = data.get('show_brand_filter',    s.show_brand_filter)
    s.show_price_filter    = data.get('show_price_filter',    s.show_price_filter)
    s.show_region_filter   = data.get('show_region_filter',   s.show_region_filter)
    s.show_rating_filter   = data.get('show_rating_filter',   s.show_rating_filter)
    s.show_weight_filter   = data.get('show_weight_filter',   s.show_weight_filter)
    s.price_min            = int(data.get('price_min',        s.price_min))
    s.price_max            = int(data.get('price_max',        s.price_max))
    s.regions_json         = data.get('regions_json',         s.regions_json)
    s.weights_json         = data.get('weights_json',         s.weights_json)
    s.page_title           = data.get('page_title',           s.page_title)
    s.whatsapp_number      = data.get('whatsapp_number',      s.whatsapp_number)
    s.save()

    return JsonResponse({'ok': True, 'message': '✅ Filter settings saved!'})




############################## Products  Urls Section Ends Here ###############################################

