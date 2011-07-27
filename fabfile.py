from fabric.api import *
from pytis.lib.utils.zipdir import zipdir

PROD = 'dcsdebica.megiteam.pl'
env.user = 'dcsdebica'

@hosts(PROD)
def deploy():
    zipdir('pytis')
    put('pytis.zip', '/home/dcsdebica/www/pytis/pytis.zip')
    run('unzip -o /home/dcsdebica/www/pytis/pytis.zip -d /home/dcsdebica/www/pytis/')
    run('restart-app pytis_v1')
    run('rm /home/dcsdebica/www/pytis.zip')