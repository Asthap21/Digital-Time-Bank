from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import RegistrationForm, LoginForm, ServiceForm , EditServiceForm
from models import db, User, Service
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.before_request
def before_request():
    pass  # Reserved for any future request hooks

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('You are already registered!', 'warning')
            return redirect(url_for('login'))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check email/password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    services = Service.query.all()
    return render_template('dashboard.html', services=services)

@app.route('/offer_service', methods=['GET', 'POST'])
@login_required
def offer_service():
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(name=form.name.data, description=form.description.data, provider=current_user)
        current_user.points += 10
        db.session.add(service)
        db.session.commit()
        flash('Service offered! You earned 10 points.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('offer_service.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

def preload_services():
    defaults = ['Tutoring', 'Cooking', 'Cleaning']
    for name in defaults:
        existing = Service.query.filter_by(name=name).first()
        if not existing:
            first_user = User.query.first()
            if first_user:
                service = Service(
                    name=name,
                    description=f"{name} service",
                    provider=first_user,
                    available=True
                )
                db.session.add(service)
    db.session.commit()

@app.route('/services')
@login_required
def services():
    services = Service.query.all()
    return render_template('services.html', services=services)

@app.route('/service/<int:service_id>')
@login_required
def view_service(service_id):
    service = Service.query.get_or_404(service_id)
    return render_template('view_service.html', service=service)

@app.route('/take_service/<int:service_id>')
@login_required
def take_service(service_id):
    service = Service.query.get_or_404(service_id)
    if service.available and service.provider != current_user:
        current_user.points -= 10
        service.provider.points += 10
        service.available = False
        db.session.commit()
        flash("You successfully took the service!", "success")
    else:
        flash("Service not available or it's your own.", "danger")
    return redirect(url_for('services'))

@app.route('/edit_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    if service.provider != current_user:
        flash("Not authorized to edit.", "danger")
        return redirect(url_for('services'))
    form = EditServiceForm(obj=service)
    if form.validate_on_submit():
        service.name = form.name.data
        service.description = form.description.data
        service.available = form.available.data
        db.session.commit()
        flash("Service updated!", "success")
        return redirect(url_for('services'))
    return render_template('edit_service.html', form=form)

@app.route('/delete_service/<int:service_id>')
@login_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    if service.provider != current_user:
        flash("Not authorized to delete.", "danger")
    else:
        db.session.delete(service)
        db.session.commit()
        flash("Service deleted!", "info")
    return redirect(url_for('services'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        preload_services()
    app.run(debug=True)

