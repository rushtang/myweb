from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,IntegerField
from wtforms.validators import  Required,Length,Email,regexp,equal_to
from wtforms import ValidationError
from  ..models import User


class LoginForm(FlaskForm):
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])
    password=PasswordField('Password',validators=[Required()])
    remeber_me=BooleanField('记住登录状态')



class RegistrationForm(FlaskForm):
    email=StringField('Email',validators=[Required(),Length(1,64),Email(message='邮箱格式不正确')])
    username=StringField("username",validators=[Required(),Length(1,64),regexp('^[A-Za-z0-9]*$'
                        ,0,'must letters or number ')])

    password=PasswordField('password',validators=[Required(),Length(1,64),equal_to('password',
                            message='password must match')])

    password2=PasswordField('confirm password',validators=[Required(),Length(1,64)])
    submit=SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('email already registered')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('username already registered')



