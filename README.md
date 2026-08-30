# ScholarVault — Academic Projects Marketplace

A Django web application for discovering, previewing, and purchasing defended university academic projects, theses, and research documents. Faculty upload materials by department; students and researchers browse the catalog, preview the first two pages for free, and unlock full documents through Paystack checkout.

## Features

- **Public catalog** — Browse and search projects by department, keyword, price, and popularity
- **Free 2-page preview** — PDF.js viewer renders the first two pages before purchase
- **Paystack payments** — Secure checkout with demo mode for local testing
- **Buyer library** — Permanent access to purchased documents with download and receipts
- **Faculty uploads** — Staff submit PDF/DOCX projects with automatic preview generation
- **Admin review workflow** — Super admins approve or reject staff submissions before publication
- **Analytics dashboards** — Revenue, downloads, lead inquiries, and moderation tools

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5.x |
| Database | SQLite (default) |
| Frontend | Tailwind CSS (CDN), Lucide icons |
| PDF preview | PDF.js, PyMuPDF |
| Payments | Paystack API |
| Documents | python-docx, ReportLab, Pillow |

## Project Structure

```
Academic_project_market_palce/
├── accounts/          # Custom user model (Buyer, Staff, Super Admin)
├── analytics/         # Dashboards, interest capture, approval workflow
├── config/            # Django settings and root URLs
├── departments/       # Academic department models and views
├── payments/          # Paystack integration, purchases, library
├── projects/          # Project materials, upload, preview, download
├── static/            # CSS and JavaScript
├── templates/         # HTML templates
├── media/             # Uploaded project files (gitignored)
├── manage.py
├── requirements.txt
└── seed_data.py       # Sample departments, users, and projects
```

## User Roles

| Role | Capabilities |
|------|--------------|
| **Buyer / Student** | Browse, preview, purchase, and download from personal library |
| **Staff** | Upload projects for their department; track sales and inquiries via staff dashboard |
| **Super Admin** | Approve/reject submissions, view platform analytics, direct-upload with auto-approval |

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Academic_project_market_palce
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (optional)

   Create a `.env` file in the project root:

   ```env
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

   PAYSTACK_PUBLIC_KEY=pk_test_your_key
   PAYSTACK_SECRET_KEY=sk_test_your_key
   PAYSTACK_DEMO_MODE=True
   ```

   When `PAYSTACK_DEMO_MODE=True`, checkout is simulated locally without real Paystack API calls.

5. **Run migrations**

   ```bash
   python manage.py migrate
   ```

6. **Seed sample data** (optional)

   ```bash
   python seed_data.py
   ```

7. **Create a superuser** (if not using seed data)

   ```bash
   python manage.py createsuperuser
   ```

8. **Start the development server**

   ```bash
   python manage.py runserver
   ```

   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | Development fallback in settings |
| `DJANGO_DEBUG` | Enable debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | `*` |
| `PAYSTACK_PUBLIC_KEY` | Paystack public API key | Placeholder |
| `PAYSTACK_SECRET_KEY` | Paystack secret API key | Placeholder |
| `PAYSTACK_DEMO_MODE` | Simulate payments locally | `True` |

## Main URLs

| Path | Description |
|------|-------------|
| `/` | Homepage |
| `/projects/` | Project catalog with filters |
| `/departments/` | Department listing |
| `/accounts/login/` | Sign in |
| `/accounts/register/` | Create account |
| `/payments/library/` | Purchased materials library |
| `/analytics/staff/` | Staff dashboard |
| `/analytics/admin/` | Super admin dashboard |
| `/admin/` | Django admin |

## Development Notes

- **Static files** — Served from `static/` during development. Run `python manage.py collectstatic` before production deployment.
- **Media files** — Uploaded project files are stored in `media/` and are not committed to git.
- **Preview generation** — On upload, the first two pages of each document are extracted automatically via PyMuPDF.
- **Full document access** — Complete files are only served to users with a successful purchase.

## License

This project is provided for academic and educational use. Add a license file if you plan to distribute or open-source it.
