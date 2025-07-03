from flask import Blueprint,send_file,render_template
import MySQLdb
import pandas as pd
from io import BytesIO

xlsx_bp=Blueprint('xlsx_bp',__name__)
db = MySQLdb.connect(host="localhost", user="root", password="hansa123456", database="employee_system")
cursor = db.cursor()

@xlsx_bp.route('/reports/employees/xlsx')
def export_employees_xlsx():
    cursor.execute("SELECT id,name,username,email,city FROM employees")
    data=cursor.fetchall()
    df=pd.DataFrame(data,columns=['ID','Name','Username','Email','City'])
    output=BytesIO()
    df.to_excel(output,index=False)
    output.seek(0)
    return send_file(output,as_attachment=True,download_name="Employees.xlsx",mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@xlsx_bp.route('/report/attendance/xlsx')
@xlsx_bp.route('/reports/attendance/xlsx')
def export_attendance_xlsx():
    cursor.execute("SELECT id, employee_id, date, sign_in, sign_out FROM attendance")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['ID', 'Employee ID', 'Date', 'Sign In', 'Sign Out'])

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="Attendance.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
