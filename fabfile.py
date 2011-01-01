from fabric.api import *
from pytis.lib.utils.zipdir import zipdir

PROD = 'dcsdebica.megiteam.pl'
env.user = 'dcsdebica'

@hosts(PROD)
def deploy():
    zipdir('pytis')
    put('pytis.zip', '~/')
    run('unzip -o pytis.zip -d /home/dcsdebica/www/pytis/')
    run('unzip -o pytis.zip -d /home/dcsdebica/www/pytis_2/')
    run('restart-app pytis_v1')
    #run('restart-app pytis_v2')
    run('rm pytis.zip')