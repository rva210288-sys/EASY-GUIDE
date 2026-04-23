from django.db import models


from .client import *
from .trip import *
from .account import *
from .chat import *


class Language(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField("ISO 639-1 code", max_length=2, primary_key=True)

    def __str__(self):
        return self.code
