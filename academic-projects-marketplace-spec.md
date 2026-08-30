# Academic Projects Marketplace — Django Web App Specification

## 1. Overview

A Django web application that allows staff (and a super admin) to upload completed and defended academic project documents (Word `.docx` or `.pdf`) organized by department. Public visitors can browse materials, filter by preference/department, preview the first 2 pages of any material, and purchase full access via Paystack. Staff and the super admin can track who downloaded or showed purchase interest in their uploaded materials.

**Core roles:**
- **Super Admin** — manages the whole platform from the Django admin panel, oversees all staff uploads, can upload materials directly (auto-approved), sees platform-wide analytics.
- **Staff** — belongs to one or more departments, uploads materials (goes into a pending-review queue), sees analytics for only their own uploads.
- **Public/Buyer** — anonymous or registered site visitor, browses materials, previews first 2 pages, purchases via Paystack.

---

## 2. Suggested App Structure

```
project_root/
├── accounts/          # custom user model, roles, auth
├── departments/       # Department model
├── projects/          # ProjectMaterial, preview generation, upload/browse views
├── payments/          # Paystack integration, Purchase model, webhook handling
├── analytics/         # Interest tracking, staff/superadmin dashboards
├── config/            # settings, urls, wsgi/asgi
└── templates/
```

Keep apps loosely coupled — `projects` should not import from `payments` directly; use signals or service functions instead.

---

## 3. Data Models

### accounts/models.py
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = "SUPERADMIN", "Super Admin"
        STAFF = "STAFF", "Staff"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)
    department = models.ForeignKey(
        "departments.Department", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="staff_members"
    )
```

### departments/models.py
```python
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
```

### projects/models.py
```python
from django.conf import settings
from django.db import models

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

    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new and self.uploaded_by.role == self.uploaded_by.Role.SUPERADMIN:
            self.status = self.Status.APPROVED
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
```

### payments/models.py
```python
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
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### analytics/models.py
```python
from django.conf import settings
from django.db import models

class Interest(models.Model):
    """Logged when a visitor previews or clicks 'I'm interested' without paying."""
    material = models.ForeignKey("projects.ProjectMaterial", on_delete=models.CASCADE, related_name="interests")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(blank=True)  # for guest interest capture
    created_at = models.DateTimeField(auto_now_add=True)

class DownloadLog(models.Model):
    """Logged every time a paid user downloads the full material."""
    material = models.ForeignKey("projects.ProjectMaterial", on_delete=models.CASCADE, related_name="downloads")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)
```

---

## 4. Roles & Permissions Logic

- Both **Staff** and **Super Admin** can upload materials (`uploaded_by` = any authenticated non-buyer user).
- Staff uploads default to `PENDING` and require Super Admin approval before appearing on the public site.
- Super Admin uploads auto-approve (handled in `ProjectMaterial.save()` above).
- Staff can only view/edit/see analytics for their **own** uploads.
- Super Admin can view/edit/see analytics for **all** uploads platform-wide, plus approve/reject staff submissions.

### Django Admin scoping (projects/admin.py)
```python
from django.contrib import admin
from .models import ProjectMaterial

@admin.register(ProjectMaterial)
class ProjectMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "uploaded_by", "status", "price", "created_at")
    list_filter = ("status", "department")
    search_fields = ("title", "abstract", "keywords")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == request.user.Role.SUPERADMIN:
            return qs
        return qs.filter(uploaded_by=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
```

If Staff will use a custom-built dashboard instead of `/admin/`, replicate this same queryset-scoping logic in the view layer (e.g. in a `LoginRequiredMixin` + `UserPassesTestMixin` class-based view, or a decorator).

---

## 5. Preview Generation Pipeline (first 2 pages)

Generate the preview **once, at upload time**, run as a background task so the upload request doesn't block:

1. On `ProjectMaterial` upload (via `post_save` signal or explicit call in the upload view):
   - If file is `.pdf` → extract first 2 pages directly using `PyMuPDF` (`fitz`) or `pypdf`.
   - If file is `.docx` → convert to PDF first using LibreOffice headless:
     ```
     soffice --headless --convert-to pdf --outdir /tmp/ input.docx
     ```
     (or a hosted conversion service like Gotenberg if LibreOffice isn't installable on the host), then extract first 2 pages from the resulting PDF.
2. Save the resulting 2-page PDF to `preview_file`.
3. Run this as a Celery task (with Redis broker) or a lighter alternative like `django-q2`/`huey` if deployment constraints (e.g. PythonAnywhere) make Celery+Redis impractical.

### Serving the preview
- Stream `preview_file` via a Django view with `Content-Disposition: inline`, ideally embedded via PDF.js in the frontend rather than a raw `<a href>` link, to add friction against easy downloading.
- **Never** expose `file` (the full document) via a static/public URL. Serve it only through a view that checks:
  ```python
  Purchase.objects.filter(user=request.user, material=material, status="SUCCESS").exists()
  ```

---

## 6. Paystack Payment Flow

1. Buyer clicks **Purchase** → server creates a `Purchase` row with `status=PENDING`, calls Paystack's **initialize transaction** endpoint, redirects buyer to the returned authorization URL.
2. Paystack redirects back to a callback URL after payment → server calls Paystack's **verify transaction** endpoint (do not trust the redirect status alone).
3. Set up a **Paystack webhook** endpoint (`/payments/webhook/`) as the source of truth for payment confirmation:
   - Verify the webhook signature using the Paystack secret key.
   - On `charge.success`, mark the matching `Purchase.status = SUCCESS`, set `paid_at`, and grant the buyer access.
4. Once `SUCCESS`, buyer sees a "Download" button that routes through the permission-checked download view (logs a `DownloadLog` entry on each download).

---

## 7. Public-Facing Site Requirements

- Browse/filter materials by department and keywords/tags.
- Material detail page shows: title, abstract, department, price, and an embedded 2-page preview (via PDF.js).
- "Purchase" CTA → Paystack checkout flow.
- Optional: "I'm interested" button for visitors not ready to buy — logs an `Interest` row (captures `email` for guests, `user` for logged-in visitors) for staff/superadmin lead-tracking.

---

## 8. Staff & Super Admin Dashboards

- **Staff dashboard**: list of their own materials with status (pending/approved/rejected), count of `Interest` and `Purchase`/`DownloadLog` entries per material.
- **Super Admin dashboard**: everything staff see, platform-wide, plus:
  - Pending-review queue for staff uploads (approve/reject with `rejection_reason`).
  - Revenue totals across all materials.
  - Ability to upload/edit/delete any material.

---

## 9. Suggested Tech Stack

- **Backend**: Django + Django REST Framework (optional, if decoupling frontend) or server-rendered templates for v1.
- **Auth**: Django's built-in auth + custom `User.role` field (no need for `django-guardian` unless per-object permissions get more complex later).
- **File preview**: `PyMuPDF` (`fitz`) or `pypdf` + LibreOffice headless (or Gotenberg) for docx→pdf conversion.
- **Background tasks**: Celery + Redis, or `django-q2`/`huey` for simpler hosting environments.
- **Payments**: Paystack REST API (initialize, verify, webhook).
- **File storage**: `django-storages` + S3-compatible storage recommended once real files accumulate — local disk (e.g. PythonAnywhere) fills up fast with private full-document storage.
- **PDF preview rendering**: PDF.js embedded in the material detail template.

---

## 10. Build Order (suggested phases for the AI coding assistant)

1. Scaffold project + apps (`accounts`, `departments`, `projects`, `payments`, `analytics`).
2. Implement custom `User` model with `role` and `department`, migrate, create initial Super Admin via `createsuperuser` + set `role=SUPERADMIN`.
3. Implement `Department` model + basic Django admin registration.
4. Implement `ProjectMaterial` model + upload form/view (staff & super admin), with the auto-approve-on-superadmin-save logic.
5. Implement Django admin scoping (`get_queryset`/`save_model` override) so staff only manage their own uploads.
6. Build the public browse/filter/detail views and templates.
7. Implement preview generation pipeline (PDF extraction + docx→pdf conversion), wired to run on upload via signal or background task.
8. Embed PDF.js preview viewer on the material detail page.
9. Implement `Purchase` model + Paystack initialize/verify/webhook flow.
10. Implement the protected full-file download view (checks `Purchase.status=SUCCESS`) + `DownloadLog` creation.
11. Implement `Interest` capture ("I'm interested" button, guest email capture).
12. Build staff dashboard (own materials + interest/purchase/download stats).
13. Build super admin dashboard (platform-wide stats + pending-review approval queue).
14. Polish: search/filter by department & keywords, pagination, basic styling.
15. Deployment prep: environment variables for Paystack keys, static/media file config, background task worker setup.

---

## 11. Open Decisions to Confirm Before/During Build

- Should Super Admin's own uploads be labeled/attributed differently on the public storefront (e.g. "Platform" listing) vs staff-attributed uploads?
- Multi-department staff: can one staff member belong to more than one department, or is it strictly one-to-one?
- Refund/dispute handling for failed or disputed Paystack transactions — out of scope for v1 or needs a model now?
- Should guests (no account) be able to purchase, or is account creation required before checkout?
