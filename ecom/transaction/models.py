from django.db import models
from django.contrib.auth.models import User
from order.models import Order

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('returned','returned'),
        ('canceled','canceled'),
        ('paid','paid')
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='ord',null=True)
    payment_method = models.CharField(max_length=255,blank=True,null=True)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'payment_id : {self.id} - {self.status}'

