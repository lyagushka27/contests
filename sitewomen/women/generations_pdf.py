# myapp/pdf_generator.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import io

def generate_certificate(user, contest_name, is_winner=False):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={"diploma" if is_winner else "certificate"}.pdf'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.drawString(100, height - 100, f"{'Диплом победителя' if is_winner else 'Сертификат участника'}")
    p.drawString(100, height - 120, f"Конкурс: {contest_name}")
    p.drawString(100, height - 140, f"Участник: {user.first_name} {user.last_name}")

    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

