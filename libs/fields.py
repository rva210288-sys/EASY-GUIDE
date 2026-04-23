import re

from django.db import models
from django.core.exceptions import ValidationError

from .choices import Choices


class MoneyField(models.DecimalField):
    DEFAULT_MAX_DIGITS = 8
    DEFAULT_DECIMAL_PLACES = 2

    def __init__(self, *args, **kwargs):
        if not kwargs.get('max_digits'):
            kwargs['max_digits'] = self.DEFAULT_MAX_DIGITS
        if not kwargs.get('decimal_places'):
            kwargs['decimal_places'] = self.DEFAULT_DECIMAL_PLACES
        super().__init__(*args, **kwargs)


class ChoicesField(models.PositiveSmallIntegerField):
    def __init__(self, *args, **kwargs):
        if isinstance(kwargs['choices'], Choices):
            kwargs['choices'] = kwargs['choices'].as_choices_list()
        super().__init__(*args, **kwargs)


class PhoneNumberField(models.CharField):
    PHONE_NUMBER_REGEX = \
        re.compile(r'^\+?([\d\-\s]{0,5}\([\d\-\s]{1,5}\))?[\d\-\s]{4,15}$')

    def __init__(self, *args, **kwargs):
        # Setting max_length = 16
        kwargs['max_length'] = 16
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        # Transforming empty to None
        if not value:
            return None

        # Checking allowed symbols with regex
        if self.PHONE_NUMBER_REGEX.match(value) is None:
            raise ValidationError("Invalid format of phone number")

        # Transforming to chosen DB standard
        value = value.replace("(", "")
        value = value.replace(")", "")
        value = value.replace("-", "")
        value = value.replace(" ", "")
        if not value.startswith("+"):
            value = "+" + value

        # Checking the length
        if len(value) < 10 or len(value) > 16:
            raise ValidationError("Invalid format of phone number")

        return value
