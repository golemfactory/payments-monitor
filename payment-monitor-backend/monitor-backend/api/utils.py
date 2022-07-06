from .models import Logs


def save_log(project, message):
    log = Logs.objects.create(project=project, message=message)
    return log
