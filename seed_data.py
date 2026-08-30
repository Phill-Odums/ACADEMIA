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

    # 1. Departments
    dept_cs, _ = Department.objects.get_or_create(
        name="Computer Science & Artificial Intelligence",
        defaults={
            'slug': 'computer-science-ai',
            'description': 'Advanced computing systems, machine learning architectures, distributed cloud computing, cybersecurity, and intelligent software systems.',
            'icon': 'cpu'
        }
    )

    dept_ee, _ = Department.objects.get_or_create(
        name="Electrical & Electronics Engineering",
        defaults={
            'slug': 'electrical-engineering',
            'description': 'Embedded IoT systems, microgrid renewable power distribution, signal processing, and robotics instrumentation.',
            'icon': 'zap'
        }
    )

    dept_econ, _ = Department.objects.get_or_create(
        name="Economics & Financial Technology",
        defaults={
            'slug': 'economics-fintech',
            'description': 'Macroeconomic forecasting models, algorithmic trading mechanisms, microfinance penetration, and econometric analyses.',
            'icon': 'trending-up'
        }
    )

    dept_med, _ = Department.objects.get_or_create(
        name="Health Sciences & Biomedical Informatics",
        defaults={
            'slug': 'health-sciences-biomedical',
            'description': 'Clinical decision support systems, epidemiology statistical models, and medical imaging diagnostics.',
            'icon': 'activity'
        }
    )

    print(f"Created/Verified {Department.objects.count()} departments.")

    # 2. Users
    # Superadmin
    admin_user, created = User.objects.get_or_create(username='admin', defaults={
        'email': 'admin@scholarvault.edu',
        'first_name': 'Super',
        'last_name': 'Administrator',
        'role': User.Role.SUPERADMIN,
        'is_staff': True,
        'is_superuser': True,
    })
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Created Super Admin: admin (password: admin123)")

    # Staff User 1
    staff_cs, created = User.objects.get_or_create(username='dr_adeyemi', defaults={
        'email': 'adeyemi.k@university.edu',
        'first_name': 'Dr. Kehinde',
        'last_name': 'Adeyemi',
        'role': User.Role.STAFF,
        'department': dept_cs,
        'bio': 'Associate Professor of Machine Intelligence and Distributed Computing.',
    })
    if created:
        staff_cs.set_password('staff123')
        staff_cs.save()
        print("Created Staff User: dr_adeyemi (password: staff123)")

    # Staff User 2
    staff_ee, created = User.objects.get_or_create(username='prof_okafor', defaults={
        'email': 'okafor.e@university.edu',
        'first_name': 'Prof. Emeka',
        'last_name': 'Okafor',
        'role': User.Role.STAFF,
        'department': dept_ee,
        'bio': 'Head of Department, Renewable Microgrid & Control Systems Engineering.',
    })
    if created:
        staff_ee.set_password('staff123')
        staff_ee.save()
        print("Created Staff User: prof_okafor (password: staff123)")

    # Buyer / Student
    buyer_user, created = User.objects.get_or_create(username='sarah_student', defaults={
        'email': 'sarah.b@student.edu',
        'first_name': 'Sarah',
        'last_name': 'Bello',
        'role': User.Role.BUYER,
        'bio': 'Undergraduate Final Year Researcher.',
    })
    if created:
        buyer_user.set_password('buyer123')
        buyer_user.save()
        print("Created Student Buyer: sarah_student (password: buyer123)")

    # 3. Project Materials
    sample_projects = [
        {
            'title': 'Autonomous Microgrid Load Balancing Using Deep Q-Learning Reinforcement Networks',
            'department': dept_ee,
            'uploaded_by': staff_ee,
            'abstract': (
                "This defended academic project designs, models, and implements an adaptive microgrid energy distribution "
                "architecture driven by Deep Q-Networks (DQN). The research investigates dynamic multi-source power integration "
                "combining solar photovoltaics, wind turbines, and localized battery storage systems. Experimental simulations "
                "conducted using IEEE 14-bus test frameworks demonstrated a 24.6% reduction in transmission line losses and a "
                "99.4% stability uptime during sudden grid disconnect scenarios."
            ),
            'keywords': 'Microgrid, Reinforcement Learning, Renewable Energy, Python, Power Systems, Deep Q-Learning',
            'price': 6500.00,
            'year_defended': 2024,
            'pages_count': 78,
            'status': ProjectMaterial.Status.APPROVED,
        },
        {
            'title': 'Federated Learning Framework for Multi-Hospital Privacy-Preserving Radiology Classification',
            'department': dept_cs,
            'uploaded_by': staff_cs,
            'abstract': (
                "Privacy-preserving machine learning presents a transformative opportunity in digital healthcare. This thesis "
                "presents a cross-silo Federated Learning protocol utilizing Differential Privacy and Secure Aggregation (SecAgg) "
                "for detecting chest anomalies from distributed X-ray scans. Trained on multi-institutional datasets comprising 42,000 "
                "scans, our approach achieves an AUC of 0.942 while guaranteeing non-leakage of raw patient records across hospital boundaries."
            ),
            'keywords': 'Federated Learning, AI, Healthcare, Radiology, Privacy, PyTorch, Convolutional Neural Networks',
            'price': 8000.00,
            'year_defended': 2024,
            'pages_count': 92,
            'status': ProjectMaterial.Status.APPROVED,
        },
        {
            'title': 'Econometric Volatility Modeling of Sovereign Bond Yields in Sub-Saharan Emerging Markets',
            'department': dept_econ,
            'uploaded_by': admin_user,
            'abstract': (
                "This study employs GARCH, EGARCH, and Markov-Switching models to investigate external macroeconomic shocks on sovereign "
                "debt yields across African capital markets between 2014 and 2023. Key findings indicate asymmetric volatility response to currency "
                "devaluation events and propose structural monetary policy intervention boundaries."
            ),
            'keywords': 'Econometrics, GARCH, Sovereign Debt, Financial Markets, Time Series, Python, Stata',
            'price': 5000.00,
            'year_defended': 2023,
            'pages_count': 64,
            'status': ProjectMaterial.Status.APPROVED,
        },
        {
            'title': 'Edge-Computing IoT Architecture for Real-Time Agricultural Soil Nutrient Monitoring',
            'department': dept_cs,
            'uploaded_by': staff_cs,
            'abstract': (
                "A low-power LoRaWAN-enabled sensor node network for continuous NPK soil nutrient sampling and predictive irrigation triggers. "
                "Includes full embedded firmware schematics, cloud telemetry broker integration, and field deployment test telemetry results."
            ),
            'keywords': 'IoT, Edge Computing, LoRaWAN, Smart Agriculture, ESP32, Embedded Systems',
            'price': 4500.00,
            'year_defended': 2024,
            'pages_count': 56,
            'status': ProjectMaterial.Status.PENDING,  # Demonstrates Pending Review Queue for Superadmin
        },
    ]

    for p_data in sample_projects:
        status_val = p_data.pop('status')
        title_val = p_data['title']
        mat, created = ProjectMaterial.objects.get_or_create(title=title_val, defaults=p_data)
        
        # Ensure sample document is written
        if created or not mat.file:
            doc_content = f"""ACADEMIC RESEARCH & DEFENDED PROJECT
TITLE: {mat.title}
DEPARTMENT: {mat.department.name}
DEFENDED YEAR: {mat.year_defended}
SUBMITTED BY: {mat.uploaded_by.get_full_name() or mat.uploaded_by.username}

ABSTRACT:
{mat.abstract}

CHAPTER 1: INTRODUCTION
The rapid expansion of specialized technologies necessitates systematic inquiry. This work addresses the critical bottleneck of scalability, reliability, and reproducible methodology.

CHAPTER 2: LITERATURE REVIEW & THEORETICAL FRAMEWORK
Previous benchmarks highlighted substantial limitations under stressed constraints. Our proposed formulation integrates resilient parameters.

CHAPTER 3: METHODOLOGY & SYSTEM DESIGN
Full algorithmic workflows, hardware architecture schematics, and analytical proofs are detailed herein.

CHAPTER 4: EXPERIMENTAL RESULTS & EVALUATION
Simulations and physical bench tests confirm high accuracy, robust fault-tolerance, and statistically significant improvements over baseline models.

CHAPTER 5: CONCLUSION & RECOMMENDATIONS FOR FUTURE SCHOLARSHIP
Comprehensive recommendations, full bibliographical citations, and source code appendices.
"""
            mat.file.save(f"full_project_{mat.id or 1}.docx", ContentFile(doc_content.encode('utf-8')), save=False)
            mat.status = status_val
            mat.save()
            generate_preview_pdf(mat)
            mat.save()
            print(f"Created project: {mat.title} (Status: {mat.status})")

    # 4. Sample Purchases & Interests
    first_approved = ProjectMaterial.objects.filter(status=ProjectMaterial.Status.APPROVED).first()
    if first_approved:
        # Purchase record
        purchase, _ = Purchase.objects.get_or_create(
            paystack_reference="APM_DEMO_REF101",
            defaults={
                'material': first_approved,
                'user': buyer_user,
                'customer_email': buyer_user.email,
                'amount_paid': first_approved.price,
                'status': Purchase.Status.SUCCESS,
                'paid_at': timezone.now(),
            }
        )
        DownloadLog.objects.get_or_create(material=first_approved, user=buyer_user)
        print(f"Created sample purchase & download log for '{first_approved.title}'")

        # Interest record
        Interest.objects.get_or_create(
            material=first_approved,
            email="prospective.researcher@mit.edu",
            defaults={'note': 'Interested in applying this methodology in our department lab.'}
        )

    print("\nDatabase seeded successfully!")
    print("Default Logins:")
    print("  Super Admin: username='admin' | password='admin123'")
    print("  Faculty Staff: username='dr_adeyemi' | password='staff123'")
    print("  Student Buyer: username='sarah_student' | password='buyer123'")

if __name__ == '__main__':
    create_seed_data()
