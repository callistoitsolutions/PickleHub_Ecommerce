
from django.shortcuts import render

from Admin_app.models import *
# Create your views here.
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt



def _hero_data(hero):
    return {
        'badge_text':        hero.badge_text,
        'title_line1':       hero.title_line1,
        'title_highlight':   hero.title_highlight,
        'title_line2':       hero.title_line2,
        'subtitle':          hero.subtitle,
        'jar_emoji':         hero.jar_emoji,
        'hero_image_url':    hero.hero_image_url,
        'buttons_json':      hero.buttons_json,
        'stats_json':        hero.stats_json,
        'float_badges_json': hero.float_badges_json,
        'is_visible':        hero.is_visible,
    }
 
def _features_data(features):
    return {
        'items_json': features.items_json,
        'is_visible': features.is_visible,
    }
 
def _category_data(category):                        # ← NEW helper
    return {
        'section_title':    category.section_title,
        'section_subtitle': category.section_subtitle,
        'items_json':       category.items_json,
        'is_visible':       category.is_visible,
    }
 
 