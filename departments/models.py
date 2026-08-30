from django.db import models
from django.utils.text import slugify

class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, default='graduation-cap', help_text="Icon identifier for UI")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def approved_materials_count(self):
        return self.materials.filter(status="APPROVED").count()

    def __str__(self):
        return self.name
