from django.core.servers.fastcgi import runfastcgi

import pinax.env


# setup the environment for Django and Pinax
pinax.env.setup_environ(__file__)


# pass off handling to FastCGI
runfastcgi(method="threaded", daemonize="false")