from django.db import models
from product.models import Product,ProductVariant
from django.contrib.auth.models import User

class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'wishlist of {self.user.username}'

class WishlistItem(models.Model):
    wishlist=models.ForeignKey(Wishlist,on_delete=models.CASCADE,related_name='wish')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def total_priced(self):
        return self.product.price * self.quantity

    def __str__(self):
        size_info = f" ({self.product_variant.size})" if self.product_variant else " (No size selected)"
        return f'{self.product.name}{size_info} in Wishlist of {self.wishlist.user.username}'   

