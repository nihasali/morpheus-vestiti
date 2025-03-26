from django.db import models

class Admin(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.username
