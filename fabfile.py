from fabricant import *

env.project = 'gitorama.com'

def dev():
    env.hosts = ['vbox']
    env.environment = 'development'
    env.project_dir = '/vagrant/gitorama.com'
    env.repository = 'git:git-private/gitorama.com.git'
    use_ssh_config(env)


def production():
    env.hosts = ['amazon']
    env.environment = 'production'
    env.project_dir = '/home/ubuntu/projects/gitorama.com'
    env.repository = '~/git-private/gitorama.com.git'
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

def make_install(
    dist='http://nodejs.org/dist/v0.6.10/node-v0.6.10.tar.gz',
    prefix='~/usr',
    check='~/usr/bin/node',
):
    pass
    # mkdir -p /tmp/build
    # cd /tmp/build
    # wget dist
    # tar zxvf node-v0.6.10.tar.gz
    # cd node-v0.6.10
    # ./configure --prefix=~/usr


def deploy():
    if env.environment == 'production':
        dir_ensure('/home/art/log/backend')

        base_dir, relative_project_dir = os.path.split(env.project_dir)
        with cd(base_dir):
            if dir_exists(relative_project_dir):
                with cd(relative_project_dir):
                    run('git pull')
            else:
                run('git clone %s %s' % (env.repository, relative_project_dir))

            with mode_sudo():
                file_attribs(
                    os.path.join(relative_project_dir, 'configs/etc/cron.d/gitorama-com.production'),
                    owner='root',
                    group='root',
                )

    create_env()

    package_ensure([
        'python-software-properties',
    ])
    sudo('add-apt-repository ppa:chris-lea/redis-server')

    package_ensure([
        'nginx',
        'redis-server',
        'python-redis',
        'g++',
    ])

    make_symlinks()
    ensure_mongo()

    # if not ~/usr/bin/npm
    #run('curl http://npmjs.org/install.sh | sh')
    # if not usr/bin/lessc
    # npm install -g less
    # npm install -g coffee-script
    upstart_ensure('nginx')
    restart()


def runserver():
    require('project_dir', provided_by=[dev])

    with cd(env.project_dir):
        local('env/bin/python app.py')


def sctl(command):
    require('project', provided_by=['dev', 'production'])
    vars = dict(command=command, project=env.project)
    run('supervisorctl -c ~/etc/supervisord.conf %(command)s %(project)s' % vars)


def restart():
    sctl('restart')

def stop():
    sctl('stop')

def start():
    sctl('start')

def status():
    sctl('status')

