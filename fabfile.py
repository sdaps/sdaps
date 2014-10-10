from fabric.api import *

env.user = 'rails'
env.hosts = ['app1.megatron.prd.atl.3dna.io', 'app2.megatron.prd.atl.3dna.io']
env.use_ssh_config = True

def deploy():
  run('cd sdaps && git pull origin master')
  run('cd sdaps && ./setup.py build')
  sudo('cd sdaps && ./setup.py install')

def setup():
  run('git clone git@github.com:3dna/sdaps.git')
