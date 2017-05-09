from flask import render_template ,redirect,request,url_for,flash
from . import auth
from .. import db
from flask_login import  login_required ,login_user,logout_user,current_user
from .forms  import LoginForm ,RegistrationForm
from ..main.forms import PostForm
from ..models import User,Permission,Post
from ..decorator import permisson_require

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()






@auth.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    print(form.email)
    return render_template('auth/login.html',form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("you have been logged out")
    return redirect(url_for('main.index'))



@auth.route("/secret")
@login_required
def secret():
    return "<h1> only authenticated users are allowed </h1>"


@auth.route("/register",methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("you can login")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)



@auth.route("/write_post",methods=['GET','POST'])
@login_required
@permisson_require(Permission.WRITE_ARTICLES)
def write_post():

    form=PostForm()

    if form.validate_on_submit() and current_user.can(Permission.WRITE_ARTICLES):
        post=Post(body=form.body.data,author_id=current_user.id,
                  title=form.title.data,digest=form.digest.data
                  )

        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('auth/write_post.html',form=form,Permission=Permission)



@auth.route("/edit_post/<int:id>",methods=['GET','POST'])
@login_required
@permisson_require(Permission.WRITE_ARTICLES)
def edit_post(id):
    onepost=Post.query.filter(Post.id==id).first()

    form=PostForm()

    if form.validate_on_submit() and current_user.can(Permission.WRITE_ARTICLES):

        onepost.title=form.title.data
        onepost.digest=form.digest.data
        onepost.body=form.body.data

        db.session.add(onepost)
        db.session.commit()
        return redirect(url_for('main.index'))

    form.title.data=onepost.title
    form.digest.data = onepost.digest
    form.body.data = onepost.body

    return render_template('auth/write_post.html',form=form,Permission=Permission)