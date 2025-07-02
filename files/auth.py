from flask import Blueprint, render_template, request, redirect, session

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user == 'admin' and pwd == 'admin123':
            session['admin'] = True
            return redirect('/main')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')
