import os, sys
sys.path.append('/home/jstpierre/music_host/MusicApp/')
os.environ['PYTHON_EGG_CACHE'] = '/usr/local/pylons/python-eggs'

from paste.deploy import loadapp

application = loadapp('config:/home/jstpierre/music_host/MusicApp/deployment.ini')