"""
ASGI config for lmw project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmw.settings.local')

application = get_asgi_application()