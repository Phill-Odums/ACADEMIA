from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = "SUPERADMIN", "Super Admin"
        STAFF = "STAFF", "Staff"
        BUYER = "BUYER", "Buyer / Student"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.BUYER)
    department = models.ForeignKey(
        "departments.Department",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="staff_members",
        help_text="Primary department for staff members"
    )
    phone_number = models.CharField(max_length=25, blank=True)
    bio = models.TextField(blank=True)

    def is_superadmin_user(self):
        return self.role == self.Role.SUPERADMIN or self.is_superuser

    def is_staff_user(self):
        return self.role in [self.Role.STAFF, self.Role.SUPERADMIN] or self.is_staff or self.is_superuser

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.SUPERADMIN
            self.is_staff = True
        elif self.role == self.Role.SUPERADMIN:
            self.is_staff = True
        elif self.role == self.Role.STAFF:
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.username
