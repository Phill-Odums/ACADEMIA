import os
import django
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from departments.models import Department
from projects.models import ProjectMaterial
from payments.models import Purchase
from analytics.models import Interest, DownloadLog
from projects.services import generate_preview_pdf
from django.utils import timezone

def create_seed_data():
    print("--- Seeding Database for Academic Projects Marketplace ---")

    # 1. Departments - All available departments for staff registration dropdown
    departments_data = [
        {
            'name': 'Biology',
            'slug': 'biology',
            'description': 'Study of living organisms, cellular processes, genetics, ecology, and evolutionary biology.',
            'icon': 'leaf'
        },
        {
            'name': 'Agriculture',
            'slug': 'agriculture',
            'description': 'Sustainable farming practices, crop science, soil management, agricultural economics, and food production systems.',
            'icon': 'sprout'
        },
        {
            'name': 'Chemistry',
            'slug': 'chemistry',
            'description': 'Organic, inorganic, analytical, physical, and medicinal chemistry research and applications.',
            'icon': 'flask-conical'
        },
        {
            'name': 'Computer Science',
            'slug': 'computer-science',
            'description': 'Software engineering, algorithms, data structures, artificial intelligence, machine learning, and computational theory.',
            'icon': 'cpu'
        },
        {
            'name': 'Biochemistry',
            'slug': 'biochemistry',
            'description': 'Chemical processes within living organisms, molecular biology, protein synthesis, and metabolic pathways.',
            'icon': 'dna'
        },
        {
            'name': 'Microbiology',
            'slug': 'microbiology',
            'description': 'Study of microorganisms, bacteria, viruses, immunology, infectious diseases, and microbial biotechnology.',
            'icon': 'microscope'
        },
        {
            'name': 'Mechanical Engineering',
            'slug': 'mechanical-engineering',
            'description': 'Thermodynamics, fluid mechanics, machine design, robotics, manufacturing processes, and mechanical systems.',
            'icon': 'cog'
        },
        {
            'name': 'Electrical Engineering',
            'slug': 'electrical-engineering',
            'description': 'Power systems, electronics, control systems, telecommunications, signal processing, and embedded systems.',
            'icon': 'zap'
        },
        {
            'name': 'Computer Engineering',
            'slug': 'computer-engineering',
            'description': 'Hardware-software integration, computer architecture, embedded systems, networking, and digital design.',
            'icon': 'hard-drive'
        },
        {
            'name': 'Mathematics',
            'slug': 'mathematics',
            'description': 'Pure and applied mathematics, statistics, calculus, algebra, mathematical modeling, and computational mathematics.',
            'icon': 'calculator'
        },
        {
            'name': 'Statistics',
            'slug': 'statistics',
            'description': 'Statistical analysis, probability theory, data science, biostatistics, econometrics, and quantitative research methods.',
            'icon': 'bar-chart-2'
        },
    ]

    created_count = 0
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={
                'slug': dept_data['slug'],
                'description': dept_data['description'],
                'icon': dept_data['icon']
            }
        )
        if created:
            created_count += 1

    print(f"Created/Verified {Department.objects.count()} departments ({created_count} newly created).")



    print("\nDatabase seeded successfully!")
    print("Default Logins:")
    print("  Super Admin: username='admin' | password='admin123'")
    print("  Faculty Staff: username='dr_adeyemi' | password='staff123'")
    print("  Student Buyer: username='sarah_student' | password='buyer123'")

if __name__ == '__main__':
    create_seed_data()
