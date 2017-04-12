from datetime import datetime
from flask import render_template,session,redirect,url_for,abort,request,current_app,\
    jsonify,flash,make_response
from flask_login import  login_required,current_user
from ..decorator import admin_require,permisson_require
from ..models import Permission,Post
from .forms import EditprofileForm,PostForm
from ..function import secure_filename,is_imgsuffix
import os


from . import main
from .forms import NameForm
from .. import db
from ..models import User

@main.route('/test')
def test():
    return render_template('test.html')



@main.route('/',methods=['GET','POST'])
def index():

    page=request.args.get('page',1,type=int)
    show_byfollowed = False
    if current_user.is_authenticated:
        show_byfollowed=bool(request.cookies.get('show_byfollowed',''))

    if show_byfollowed:
        query=current_user.byfollowed_posts
    else:
        query=Post.query

    pagination=query.order_by(Post.timestamp.desc()).paginate(page,per_page=10,error_out=False)
    posts = pagination.items

    return render_template('index.html',posts=posts,Permission=Permission,pagination=pagination,show_byfollowed=show_byfollowed)

#查询所有文章或者关注者的文章
@main.route('/all')
@login_required
def show_all():
    resp=make_response(redirect(url_for('.index')))
    resp.set_cookie('show_byfollowed','',max_age=30*24*60*60)
    return resp

@main.route('/byfollowed')
@login_required
def show_byfollowed():
    resp=make_response(redirect(url_for('.index')))
    resp.set_cookie('show_byfollowed','1',max_age=30*24*60*60)
    return resp

@main.route('/follow/<username>')
@login_required
@permisson_require(Permission.FOLLOW)
def follow(username):
    user=User.query.filter_by(username=username).first()
    current_user.follow(user)
    flash('you are now following {}'.format(username))
    return redirect(url_for('.user',username=username))



@main.route('/unfollow/<username>')
@login_required
@permisson_require(Permission.FOLLOW)
def unfollow(username):
    user=User.query.filter_by(username=username).first()
    current_user.unfollow(user)
    flash('you are now unfollowing {}'.format(username))
    return redirect(url_for('.user',username=username))


@main.route('/post/<int:id>')
def post(id):
    onepost=Post.query.filter(Post.id==id).first()

    return render_template('post.html',onepost=onepost)


@main.route('/article')
def article():
    page = request.args.get('page', 1, type=int)
    query = Post.query.filter(Post.author_id==1)

    pagination = query.order_by(Post.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    posts = pagination.items

    return render_template('article.html', posts=posts, Permission=Permission, pagination=pagination)









@main.route('/secert')
@login_required
def secret():
    return 'allowed'



@main.route('/admin')
@login_required
@admin_require
def for_admins_only():
    return "for administrator"


@main.route('/moderator')
@login_required
@permisson_require(Permission.MODERATE_COMMENTS)
def for_moderator_only():
    return "for comment moderators"



@main.route('/follow')
@login_required
@permisson_require(Permission.FOLLOW)
def for_follow_only():
    return "for comment FOLLOW"


@main.route('/user/<username>')
def user(username):
    page = request.args.get('page', 1, type=int)
    user=User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    pagination = user.post_list.order_by(Post.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    posts = pagination.items

    return render_template('user.html',user=user,posts=posts,Permission=Permission,pagination=pagination)








@main.route('/editprofile',methods=['GET','POST'])
@login_required
def editprofile():
    form=EditprofileForm()
    if form.validate_on_submit():
        current_user.name=request.form['name']
        current_user.location=request.form['location']
        current_user.about_me=form.about_me.data
        current_user.email=form.email.data
        f=form.head_portrait.data
        user='init'
        while user is not None:
            filename = secure_filename(f.filename)
            user = User.query.filter_by(head_portrait=filename).first()

        if f is not None and is_imgsuffix(f.filename):
            f.save(current_app.config['head_portrait'.upper()]+filename)
            current_user.head_portrait=filename
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('.user',username=current_user.username))

    form.name.data=current_user.name
    form.about_me.data=current_user.about_me
    form.location.data=current_user.location
    form.email.data=current_user.email

    return render_template('editprofile.html',form=form)





