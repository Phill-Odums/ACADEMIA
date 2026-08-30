import os
from django.conf import settings
from django.db import models
from django.urls import reverse

class ProjectMaterial(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending Review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    title = models.CharField(max_length=255)
    department = models.ForeignKey("departments.Department", on_delete=models.PROTECT, related_name="materials")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="uploads")
    abstract = models.TextField()
    keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags for search/filtering")

    file = models.FileField(upload_to="projects/full/")          # private, never served directly
    preview_file = models.FileField(upload_to="projects/preview/", blank=True, null=True)  # auto-generated, first 2 pages

    price = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    rejection_reason = models.TextField(blank=True)

    year_defended = models.PositiveIntegerField(default=2024, help_text="Year project was defended")
    pages_count = models.PositiveIntegerField(default=45, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new and self.uploaded_by:
            if getattr(self.uploaded_by, 'role', '') == 'SUPERADMIN' or self.uploaded_by.is_superuser:
                self.status = self.Status.APPROVED
        super().save(*args, **kwargs)

    @property
    def keyword_list(self):
        if not self.keywords:
            return []
        return [k.strip() for k in self.keywords.split(',') if k.strip()]

    @property
    def file_extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1].lower().replace('.', '')
        return 'pdf'

    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'pk': self.pk})

    def total_purchases(self):
        return self.purchases.filter(status="SUCCESS").count()

    def total_revenue(self):
        return sum(p.amount_paid for p in self.purchases.filter(status="SUCCESS"))

    def total_interests(self):
        return self.interests.count()

    def total_downloads(self):
        return self.downloads.count()

    def __str__(self):
        return self.title
