# myapp/pdf_generator.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfbase.pdfmetrics import stringWidth

def generate_certificate(user, contest_name, is_winner=False):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={"diploma" if is_winner else "certificate"}.pdf'

    # Загружаем шаблон
    template_name = "диплом.pdf" if is_winner else "сертификат.pdf"
    template_path = os.path.join(settings.BASE_DIR, 'women/static/images', template_name)
    
    # Создаем новый PDF поверх шаблона
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    width, height = letter
    
    # Загружаем шрифт
    font_path = os.path.join(settings.BASE_DIR, 'women/static/fonts/arial.ttf')
    pdfmetrics.registerFont(TTFont('Arial', font_path))
    can.setFont('Arial', 14)
    
    # Центрируем текст
    def center_text(text, y):
        text_width = stringWidth(text, 'Arial', 14)
        x = (width - text_width) / 2
        can.drawString(x, y, text)
    
    # Добавляем текст на шаблон
    # Координаты нужно подобрать в зависимости от вашего шаблона
    center_text(f"{user.first_name} {user.last_name}", 540)
    center_text(contest_name, 340)
    
    can.save()
    
    # Перемещаемся в начало потока
    packet.seek(0)
    new_pdf = PdfReader(packet)
    
    # Читаем существующий PDF
    existing_pdf = PdfReader(open(template_path, "rb"))
    output = PdfWriter()
    
    # Добавляем "водяной знак" (наш текст) на первую страницу
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)
    
    # Сохраняем результат
    output_stream = io.BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    
    response.write(output_stream.getvalue())
    output_stream.close()
    
    return response

