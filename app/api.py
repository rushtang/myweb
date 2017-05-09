from flask import request,redirect,url_for,render_template
from flask_jsonrpc import JSONRPC
from flask_jsonrpc.exceptions import Error,OtherError
from werkzeug.datastructures import MultiDict
from .manage import app
from .auth.forms import LoginForm
from flask_login import login_user
from .models import User


jsonrpc = JSONRPC(app, service_url='/api')

@jsonrpc.method('test')
def test():
    testerror=OtherError(message='我觉得是错误的')
    return testerror.json_rpc_format


@jsonrpc.method('login')
def login(**kwargs):
    json=request.get_json()

    form=LoginForm()
    form.email.data=json['params'].get('email')
    form.password.data = json['params'].get('password')
    form.remeber_me.data=json['params'].get('remeber_me')
    form.csrf_token.data = json['params'].get('csrf_token')

    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is  None:
            error = OtherError(message="账号不存在！")
            return error.json_rpc_format
        if user.verify_password(form.password.data) is False:
            error = OtherError(message="错误的密码！")
            return error.json_rpc_format

        login_user(user,form.remeber_me.data)
        return {"rs":'ok'}

    error = OtherError(message=form.errors)
    return error.json_rpc_format
