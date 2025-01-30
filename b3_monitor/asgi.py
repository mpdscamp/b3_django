import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'b3_monitor.settings')

application = get_asgi_application()
