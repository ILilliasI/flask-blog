from flask import render_template, url_for, flash, redirect, request, abort

from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, PostForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", blogs=Post.query.all())


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash(f'Account created for { form.username.data }!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            flash(f'You have been logged in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your e-mail and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def create_new_post():
    form = PostForm()

    if form.validate_on_submit():
        new_post = Post(title=form.title.data, content=form.content.data,
                        author=current_user)
        db.session.add(new_post)
        db.session.commit()

        flash('The post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form)


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
    current_post = Post.query.get_or_404(post_id)

    return render_template('post.html', title=current_post.title, post=current_post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post_to_update = Post.query.get_or_404(post_id)

    if post_to_update.author != current_user:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post_to_update.title = form.title.data
        post_to_update.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post_to_update.id))
    elif request.method == 'GET':
        form.title.data = post_to_update.title
        form.content.data = post_to_update.content

    return render_template('create_post.html', title='Update Post', form=form)


@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)
    print(post_to_delete.author)
    if post_to_delete.author != current_user:
        abort(403)
    db.session.delete(post_to_delete)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))
