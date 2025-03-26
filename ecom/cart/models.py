from django.db import models
from django.contrib.auth.models import User
from product.models import Product

class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

class Cartitems(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='cart_items')
    product =  models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    quantity = models.PositiveIntegerField(default=0)
    size = models.CharField(max_length=10,default='M',null=True,blank=True)

    def total_price(self):
        return self.product.price*self.quantity

    def __str__(self):
        return super().__str__()
