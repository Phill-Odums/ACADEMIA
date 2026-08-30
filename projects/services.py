import os
import io
from pathlib import Path
from django.core.files.base import ContentFile
from django.conf import settings

def generate_preview_pdf(material_instance):
    """
    Generates a 2-page PDF preview for the uploaded ProjectMaterial instance.
    Uses pypdf, PyMuPDF (fitz), or reportlab.
    """
    if not material_instance.file:
        return False

    file_path = material_instance.file.path
    ext = os.path.splitext(file_path)[1].lower()
    preview_bytes = None

    try:
        if ext == '.pdf':
            # Try pypdf first
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                writer = pypdf.PdfWriter()
                pages_to_add = min(2, len(reader.pages))
                for i in range(pages_to_add):
                    writer.add_page(reader.pages[i])
                
                buffer = io.BytesIO()
                writer.write(buffer)
                preview_bytes = buffer.getvalue()
                buffer.close()
            except ImportError:
                # Try fitz
                import fitz
                doc = fitz.open(file_path)
                num_pages = min(2, len(doc))
                preview_doc = fitz.open()
                preview_doc.insert_pdf(doc, from_page=0, to_page=num_pages - 1)
                preview_bytes = preview_doc.write()
                preview_doc.close()
                doc.close()

        elif ext in ['.docx', '.doc']:
            # Try reading docx text
            full_text = ""
            try:
                import docx
                doc = docx.Document(file_path)
                full_text = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            except Exception:
                full_text = f"Title: {material_instance.title}\n\nAbstract:\n{material_instance.abstract}"

            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            buffer = io.BytesIO()
            pdf_doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=54,
                leftMargin=54,
                topMargin=54,
                bottomMargin=54
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=18,
                leading=22,
                textColor=colors.HexColor('#1E293B'),
                spaceAfter=12
            )
            meta_style = ParagraphStyle(
                'MetaStyle',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#64748B'),
                spaceAfter=18
            )
            body_style = ParagraphStyle(
                'BodyStyle',
                parent=styles['Normal'],
                fontSize=11,
                leading=16,
                textColor=colors.HexColor('#334155'),
                spaceAfter=10
            )

            story = [
                Paragraph(f"<b>[PREVIEW - 2 PAGES]</b> {material_instance.title}", title_style),
                Paragraph(f"Department: {material_instance.department.name} | Defended Academic Work ({material_instance.year_defended})", meta_style),
                Spacer(1, 10),
                Paragraph("<b>Abstract & Summary:</b>", styles['Heading3']),
                Spacer(1, 6),
                Paragraph(material_instance.abstract.replace("\n", "<br/>"), body_style),
                Spacer(1, 14),
                Paragraph("<b>Project Work Excerpt:</b>", styles['Heading3']),
                Spacer(1, 6),
            ]

            paragraphs = [p for p in full_text.split("\n\n") if p.strip()][:8]
            for p in paragraphs:
                clean_p = p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(clean_p, body_style))
                story.append(Spacer(1, 8))

            pdf_doc.build(story)
            preview_bytes = buffer.getvalue()
            buffer.close()

    except Exception as e:
        print(f"Preview generation error: {e}")

    # Fallback to reportlab abstract sheet if needed
    if not preview_bytes:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            buffer = io.BytesIO()
            pdf_doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
            styles = getSampleStyleSheet()
            story = [
                Paragraph(f"<b>[PREVIEW] {material_instance.title}</b>", styles['Heading1']),
                Paragraph(f"Department: {material_instance.department.name} | Defended {material_instance.year_defended}", styles['Normal']),
                Spacer(1, 15),
                Paragraph("<b>Abstract:</b>", styles['Heading2']),
                Paragraph(material_instance.abstract.replace("\n", "<br/>"), styles['Normal']),
            ]
            pdf_doc.build(story)
            preview_bytes = buffer.getvalue()
            buffer.close()
        except Exception:
            return False

    if preview_bytes:
        filename = f"preview_{material_instance.id or 'temp'}_{Path(file_path).stem}.pdf"
        material_instance.preview_file.save(filename, ContentFile(preview_bytes), save=False)
        return True

    return False
