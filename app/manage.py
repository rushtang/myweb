#!/usr/bin/env python

import os
from app import create_app,db
from app.models import User,Role,Post,Follow
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand
from flask_jsonrpc.proxy  import ServiceProxy


app=create_app('default')


manager=Manager(app)
migrate=Migrate(app,db)
server = ServiceProxy('http://127.0.0.1:5000/api')

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role,Post=Post,Follow=Follow,server=server)

manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)

@manager.command
def deploy():
    from flask_migrate import upgrade

    upgrade()

    from app.models import User, Role
    Role.insert_roles()









