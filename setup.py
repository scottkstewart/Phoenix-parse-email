import os
from distutils.core import setup
setup(name='PPE',
      version='1.0',
      description='Phoenix-Parse-Email',
      author='Scott Stewart',
      author_email='scottkstewart16@gmail.com',
      requires=['beautifulsoup4', 'requests', 'lxml', 'daemonize', 'dbm-gnu']
      py_modules=['ppeMod'])
os.system("mkdir /etc/ppe; touch /etc/ppe/log; touch /etc/ppe/runlog; chmod 777 -Rf /etc/ppe; cp phoenix /usr/bin/phoenix")
