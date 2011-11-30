from fabric.api import *
from cuisine import *

def dev():
    env.hosts = ['vbox']
    env.type = 'development'
    env.project_dir = '/vagrant/gitorama.com'
    use_ssh_config(env)

def create_env():
    with cd(env.project_dir):
        if not dir_exists('env'):
            run('virtualenv env')
        run('env/bin/pip install -r requirements.txt')


def setup():
    create_env()

def run_server():
    with cd(env.project_dir):
        run('env/bin/python app.py')

