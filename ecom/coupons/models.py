from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    discount_value = models.IntegerField()
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField()
    active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=1)
    created_at = models.DateField(auto_now_add=True)

    def is_valid(self):
        """Check if the coupon is active and within the validity period."""
        today = timezone.now().date()
        return self.active and self.valid_from <= today <= self.valid_to

    def __str__(self):
        return self.code