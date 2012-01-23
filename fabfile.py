from fabricant import *


def dev():
    env.hosts = ['vbox']
    env.environment = 'development'
    env.project_dir = '/vagrant/gitorama.com'
    use_ssh_config(env)


def create_env():
    with cd(env.project_dir):
        if not dir_exists('env'):
            run('virtualenv env')
        run('env/bin/pip install -r requirements/%s.txt' % env.environment)


def ensure_apt_source(source_line):
    if not run("grep '%s' /etc/apt/sources.list >& /dev/null && echo OK ; true" % source_line).endswith('OK'):
        sudo("echo '%s' >> /etc/apt/sources.list" % source_line)


def ensure_mongo():
    if not command_check('mongod'):
        sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
        ensure_apt_source('deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen')
        sudo("apt-get --yes update")
        package_ensure(['mongodb-10gen'])

    upstart_ensure('mongodb')


def setup():
    create_env()
    make_symlinks()
    ensure_mongo()


def runserver():
    require('project_dir', provided_by=[dev])

    with cd(env.project_dir):
        local('env/bin/python app.py')

