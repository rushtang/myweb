#!/usr/bin/env python

import os
from app import create_app,db
from app.models import User,Role,Post,Follow
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

app=create_app('production')
manager=Manager(app)
migrate=Migrate(app,db)

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role,Post=Post,Follow=Follow)

manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)

@manager.command
def deploy():
    from flask_migrate import upgrade

    upgrade()

    from app.models import User, Role
    Role.insert_roles()





if __name__=='__main__':
    manager.run()

