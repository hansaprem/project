from flask import Blueprint, send_file
from fpdf import FPDF
import MySQLdb
import qrcode,os
from PIL import Image
from io import BytesIO

pdf_bp = Blueprint('pdf_bp', __name__)
db = MySQLdb.connect(host="localhost", user="root", password="hansa123456", database="employee_system")
cursor = db.cursor()


@pdf_bp.route('/reports/employees/pdf')
def export_employees_pdf():
    cursor.execute("SELECT id, name, username, email, city FROM employees")
    data = cursor.fetchall()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Employee Report", ln=True, align='C')

    col_widths = [10, 40, 35, 60, 30]
    headers = ['ID', 'Name', 'Username', 'Email', 'City']

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1)
    pdf.ln()

    for row in data:
        for i, item in enumerate(row):
            pdf.cell(col_widths[i], 10, str(item), border=1)
        pdf.ln()

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_stream = BytesIO(pdf_bytes)

    return send_file(pdf_stream, as_attachment=True, download_name="employees.pdf", mimetype="application/pdf")


@pdf_bp.route('/reports/attendance/pdf')
def export_attendance_pdf():
    cursor.execute("SELECT id, employee_id, date, sign_in, sign_out FROM attendance")
    data = cursor.fetchall()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Attendance Report", ln=True, align='C')

    col_widths = [10, 30, 40, 40, 40]
    headers = ['ID', 'Emp ID', 'Date', 'Sign In', 'Sign Out']

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1)
    pdf.ln()

    for row in data:
        for i, item in enumerate(row):
            pdf.cell(col_widths[i], 10, str(item), border=1)
        pdf.ln()

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_stream = BytesIO(pdf_bytes)

    return send_file(pdf_stream, as_attachment=True, download_name="attendance.pdf", mimetype="application/pdf")

@pdf_bp.route('/reports/employee_cards/pdf')
def employee_cards_pdf():
    cursor.execute("SELECT id, name, username, photo FROM employees")
    data = cursor.fetchall()

    pdf = FPDF()
    for emp in data:
        emp_id, name, username, photo = emp
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 10, f"Employee Card - {name}", ln=True, align='C')

        if photo:
            pdf.image(f"static/uploads/{photo}", x=10, y=30, w=40, h=40)

        qr_img = qrcode.make(str(username))
        qr_path = f"static/temp_qr/{username}.png"
        qr_img.save(qr_path)
        pdf.image(qr_path, x=60, y=30, w=40, h=40)
        os.remove(qr_path)

        pdf.ln(60)
        pdf.cell(100, 10, f"Name: {name}", ln=True)
        pdf.cell(100, 10, f"Username: {username}", ln=True)

    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="employee_cards.pdf", mimetype="application/pdf")