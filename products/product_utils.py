
from django.shortcuts import render
import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.core.paginator import Paginator
from django.utils.text import slugify
from products.models import *
from Admin_app.models import *




def _product_page_data(settings):
    return {
        'show_category_filter': settings.show_category_filter,
        'show_brand_filter':    settings.show_brand_filter,
        'show_price_filter':    settings.show_price_filter,
        'show_region_filter':   settings.show_region_filter,
        'show_rating_filter':   settings.show_rating_filter,
        'show_weight_filter':   settings.show_weight_filter,
        'price_min':            settings.price_min,
        'price_max':            settings.price_max,
        'regions_json':         settings.regions_json,
        'weights_json':         settings.weights_json,
        'page_title':           settings.page_title,
        'whatsapp_number':      settings.whatsapp_number,
    }

