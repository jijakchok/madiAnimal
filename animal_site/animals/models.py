from django.db import models
from django.utils import timezone

class Animal(models.Model):
    image = models.ImageField(upload_to='animals/')
    date = models.DateTimeField(default=timezone.now, db_index=True)
    comment = models.TextField()
    number = models.IntegerField(blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Animal {self.id}"

    class Meta:
        ordering = ['-date']