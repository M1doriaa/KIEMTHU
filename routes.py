from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from models import User, TaxRecord
from forms import RegistrationForm, LoginForm, TaxForm
from werkzeug.security import generate_password_hash, check_password_hash

def calculate_tax(income, dependents):
    giam_tru_gia_canh = 11000000
    giam_tru_nguoi_phu_thuoc = 4400000
    thu_nhap_chiu_thue = income - giam_tru_gia_canh - (giam_tru_nguoi_phu_thuoc * dependents)
    if thu_nhap_chiu_thue <= 0:
        return 0
    if thu_nhap_chiu_thue <= 5000000:
        thue_phai_nop = thu_nhap_chiu_thue * 0.05
    elif thu_nhap_chiu_thue <= 10000000:
        thue_phai_nop = thu_nhap_chiu_thue * 0.1 - 250000
    elif thu_nhap_chiu_thue <= 18000000:
        thue_phai_nop = thu_nhap_chiu_thue * 0.15 - 750000
    elif thu_nhap_chiu_thue <= 32000000:
        thue_phai_nop = thu_nhap_chiu_thue * 0.2 - 1650000
    elif thu_nhap_chiu_thue <= 52000000:
        thue_phai_nop = thu_nhap_chiu_thue * 0.25 - 3250000
    elif thu_nhap_chiu_thue <= 80000000:
        thue_phai_nop = thu_nhap_chiu_thue * 0.3 - 5850000
    else:
        thue_phai_nop = thu_nhap_chiu_thue * 0.35 - 9850000
    return thue_phai_nop

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html', title='Home')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/calculate_tax", methods=['GET', 'POST'])
@login_required
def calculate_tax_view():
    form = TaxForm()
    tax_result = None
    if form.validate_on_submit():
        income = form.income.data
        dependents = form.dependents.data
        tax_result = calculate_tax(income, dependents)
        tax_record = TaxRecord(income=income, dependents=dependents, tax=tax_result, user=current_user)
        db.session.add(tax_record)
        db.session.commit()
        flash('Tax calculated and saved!', 'success')
    return render_template('calculate_tax.html', title='Calculate Tax', form=form, tax_result=tax_result)

@app.route("/tax_list")
@login_required
def tax_list():
    tax_records = TaxRecord.query.filter_by(user_id=current_user.id).all()
    return render_template('tax_list.html', title='Tax Records', tax_records=tax_records)
