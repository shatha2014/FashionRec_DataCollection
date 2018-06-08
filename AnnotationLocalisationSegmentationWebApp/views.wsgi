#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/annotation_webapp/")

from views import annotation_app as application
application.secret_key = 'thefoxjumpoverthelazydog'
