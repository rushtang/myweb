from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_pagedown.fields import PageDownField
from wtforms import StringField,TextAreaField,SubmitField,ValidationError
from wtforms.validators import Required,Length,Email
from ..models import User

class NameForm():
    pass


class EditprofileForm(FlaskForm):
    name=StringField('real name',validators=[Length(2,20,message='2到10')])
    location=StringField("location",validators=[Length(1,64)])
    about_me=TextAreaField('about_me',validators=[Required(message='必选')])
    email=StringField('email',validators=[Required(message='必选'),Email(message='请输入邮箱')])
    head_portrait=FileField('head_portrait')
    submit=SubmitField('submit')

    def validate_email(self,field):
        user=User.query.filter_by(email=field.data).first()
        if user is None and user.email.data!=current_user.email.data:
            raise ValidationError(message="该邮箱已被其他人注册")


class PostForm(FlaskForm):
    title=StringField('title',validators=[Required(message='不能为空'),Length(1,30,message='不能超过30字')])
    digest = StringField('digest', validators=[ Required(message='不能为空'),Length(1, 100, message='不能超过100字')])
    body=PageDownField('body',validators=[Required(message='不能为空'),Length(1,2000,message='不能超过2000字')])
    submit=SubmitField('submit')




