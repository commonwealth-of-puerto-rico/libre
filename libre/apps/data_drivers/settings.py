from django.conf import settings

SCHEDULER_RESOLUTION = getattr(settings, 'DATA_DRIVER_SCHEDULER_RESOLUTION')
LQL_DELIMITER = getattr(settings, 'LQL_DELIMITER')
