from django.conf import settings
from django.db import models

class Purchase(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    material = models.ForeignKey("projects.ProjectMaterial", on_delete=models.CASCADE, related_name="purchases")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchases")
    paystack_reference = models.CharField(max_length=100, unique=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    customer_email = models.EmailField(blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def is_successful(self):
        return self.status == self.Status.SUCCESS

    def __str__(self):
        return f"{self.user.username} - {self.material.title} ({self.status})"
