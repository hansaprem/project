from flask import Flask
from config import *
from files.auth import auth_bp
from files.employee import emp_bp
from files.attendance import att_bp
from files.dashboard import dash_bp
from files.reports_xlsx import xlsx_bp
from files.reports_pdf import pdf_bp
from files.reports_show import report_page_bp

app = Flask(__name__)
app.secret_key = 'project123'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

app.register_blueprint(auth_bp)
app.register_blueprint(emp_bp)
app.register_blueprint(att_bp)
app.register_blueprint(dash_bp)
app.register_blueprint(xlsx_bp)
app.register_blueprint(pdf_bp)
app.register_blueprint(report_page_bp)

if __name__ == '__main__':
    app.run(debug=True)
