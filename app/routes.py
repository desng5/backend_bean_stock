from app import app, db
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .forms import RegisterForm, LoginForm, CoffeeForm
from .models import User, Coffee

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        user_check = db.session.execute(db.select(User).where((User.username == username) | (User.email == email))).scalars().all()
        if user_check:
            flash('That username and/or email address is already registered', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash(f'{username} has been registered!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = db.session.execute(db.select(User).where(User.email==email)).scalars().one_or_none()
        if user is not None and user.check_password(password):
            login_user(user)
            flash(f'Successfully logged in with {email}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email and/or password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have successfully logged out', 'primary')
    return redirect(url_for('index'))

@app.route('/create', methods=['GET','POST'])
@login_required
def create_coffee():
    form = CoffeeForm()
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        description = form.description.data
        rating = form.rating.data
        brew_method = form.brew_method.data
        roaster = form.roaster.data

        new_coffee = Coffee(name=name, price=price, description=description, rating=rating, brew_method=brew_method, roaster=roaster, user_id=current_user.id)
        db.session.add(new_coffee)
        db.session.commit()
        flash(f'You have brewed the {new_coffee.name} coffee!', 'success')
        return redirect(url_for('index'))

    return render_template('create.html', form=form)

@app.route('/edit/<coffee_id>', methods=['GET', 'POST'])
@login_required
def edit_coffee(coffee_id):
    coffee = db.session.get(Coffee, coffee_id)
    if coffee is None:
        flash(f'The coffee with an ID of {coffee_id} does not exist', 'danger')
        return redirect(url_for('index'))
    elif coffee.brewer != current_user:
        flash('You do not have permission to edit this coffee', 'danger')
        return redirect(url_for('index'))

    form = CoffeeForm()
    if form.validate_on_submit():
        coffee.name = form.name.data
        coffee.price = form.price.data
        coffee.description = form.description.data
        coffee.rating = form.rating.data
        coffee.brew_method = form.brew_method.data
        coffee.roaster = form.roaster.data

        db.session.commit()
        flash(f'{coffee.name} has been edited.', 'success')
        return redirect(url_for('index'))

    form.name.data = coffee.name
    form.price.data = coffee.price
    form.description.data = coffee.description
    form.rating.data = coffee.rating
    form.brew_method.data = coffee.brew_method
    form.roaster.data = coffee.roaster

    return render_template('edit.html', form=form, coffee=coffee)

@app.route('/delete/<coffee_id>')
@login_required
def delete_coffee(coffee_id):
    coffee = db.session.get(Coffee, coffee_id)
    if coffee is None:
        flash(f'Coffee with an ID of {coffee_id} does not exist', 'danger')
        return redirect(url_for('index'))
    elif coffee.brewer != current_user:
        flash('You do not have permission to delete this coffee', 'danger')
        return redirect(url_for('index'))

    db.session.delete(coffee)
    db.session.commit()
    flash(f'Your {coffee.name} coffee has been deleted', 'success')
    return redirect(url_for('index'))