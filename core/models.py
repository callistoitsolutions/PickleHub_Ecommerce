
from django.db import models
from Admin_app.models import *
from products.models import *

############# Cart Modal Starts Here ##################################
class Cart(models.Model):
    # Links to the User Table
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE, related_name='user_cart')
    
    # Coupon Fields (For Future Use)
    coupon_code = models.CharField(max_length=50, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Cart of {self.user.user_name}"

    @property
    def final_total(self):
        # Calculates (Sum of Items) - Discount
        subtotal = sum(item.item_total for item in self.cart_items.all())
        return subtotal - self.discount_amount
    
################ Cart Modal Ends Here #####################################


############## Cart Item Modal Starts Here #############################

class CartItem(models.Model):
    # Links to the Cart (Parent)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField(default=1)
    
    # We store the price at the time of adding to cart 
    # (In case the product price changes later)
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def item_total(self):
        return self.price_at_addition * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
############## Cart Item Modal Ends Here ####################################