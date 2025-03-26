from django.db import models
from cloudinary.models import CloudinaryField
from admin_category.models import Categories

class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    original_price = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    category_id = models.ForeignKey(Categories,related_name='product',on_delete=models.CASCADE)
    image1 = CloudinaryField('image',null=True,blank=True)
    image2 = CloudinaryField('image',null=True,blank=True)
    image3 = CloudinaryField('image',null=True,blank=True)
    offer = models.DecimalField(max_digits=7,decimal_places=2,null=True,blank=True,default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def calculate_final_price(self):

        product_discount = (self.offer/100) * self.original_price if self.offer else 0
        category_discount = (self.category_id.cat_offer / 100) * self.original_price if self.category_id.cat_offer else 0
        max_dicount = max(product_discount,category_discount)

        return self.original_price - max_dicount

    def save(self,*args,**kwargs):
        if not self.original_price:
            self.original_price = self.price

        self.price = self.calculate_final_price()
        super().save(*args,**kwargs)

class ProductVariant(models.Model):
    product = models.ForeignKey(Product,related_name='variant',on_delete=models.CASCADE)
    size = models.CharField(max_length=50,blank=True,null=True)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.stock}"

