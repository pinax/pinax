
from datetime import datetime

from django.db import models


class WaitingListEntry(models.Model):
    email = models.EmailField(unique=True)
    created = models.DateTimeField(default=datetime.now, editable=False)
