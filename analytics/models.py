from django.conf import settings
from django.db import models

class Interest(models.Model):
    """Logged when a visitor previews or clicks 'I'm interested'."""
    material = models.ForeignKey("projects.ProjectMaterial", on_delete=models.CASCADE, related_name="interests")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="interests")
    email = models.EmailField(blank=True, help_text="Captured email for guest visitors")
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        ident = self.user.username if self.user else (self.email or "Anonymous")
        return f"Interest: {ident} on {self.material.title}"

class DownloadLog(models.Model):
    """Logged every time a paid user downloads the full material."""
    material = models.ForeignKey("projects.ProjectMaterial", on_delete=models.CASCADE, related_name="downloads")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="downloads")
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-downloaded_at']

    def __str__(self):
        return f"Download: {self.user.username} - {self.material.title}"
