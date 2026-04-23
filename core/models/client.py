from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.utils import timezone

from libs.choices import Choices
from libs.fields import ChoicesField, PhoneNumberField

from .account import Account


class ClientManager(models.Manager):
    @transaction.atomic
    def create(self, email, password, first_name, last_name):
        # We ensure the creation of related user
        username = email
        user = User.objects.create_user(username, email, password,
                                        first_name=first_name,
                                        last_name=last_name)
        return super().create(user=user)


class Client(models.Model):
    LANGUAGE_DEFAULT = 'en'
    SEXES = Choices(
        _('female'),
        _('male'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                primary_key=True)

    guide_profile = models.OneToOneField('GuideProfile',
                                         on_delete=models.SET_NULL, null=True,
                                         default=None, blank=True)

    account = models.OneToOneField('Account', on_delete=models.CASCADE,
                                   blank=True)

    sex = ChoicesField(choices=SEXES, null=True, default=None, blank=True)
    dob = models.DateField(null=True, default=None, blank=True)
    phone = PhoneNumberField(null=True, default=None, blank=True)
    language = models.ForeignKey('Language', on_delete=models.SET_DEFAULT,
                                 default=LANGUAGE_DEFAULT)
    country = models.CharField(max_length=30, default="", blank=True)
    city = models.CharField(max_length=30, default="", blank=True)
    about = models.TextField(default="", blank=True)
    additional = models.TextField(default="", blank=True)
    languages_speak = models.ManyToManyField('Language', blank=True,
                                             related_name='languages_speak')
    has_driving_license = models.BooleanField(default=False)
    driving_experience = models.PositiveIntegerField(null=True, default=None,
                                                     blank=True)

    avatar = models.ImageField(upload_to='avatar', null=True, default=None,
                               blank=True)

    objects = ClientManager()

    def __str__(self):
        return self.user.username

    def is_guide(self):
        return self.guide_profile is not None
    is_guide.boolean = True

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Creating account for new client
        if self._state.adding and self.account_id is None:
            self.account = Account.objects.create()

        return super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self):
        # Deleting related account
        self.account.delete()

        # We need to delete the related self.user,
        # so we delete self.user only, the client will be deleted by DB
        # because of on_delete=models.CASCADE for user field
        if not self.user.is_staff:
            self.user.delete()
        else:
            super().delete()

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return None

    @property
    def age(self):
        if self.dob:
            today = timezone.now()
            delta_year = today.year - self.dob.year
            amendment = int((today.month, today.day) <
                            (self.dob.month, self.dob.day))
            return delta_year - amendment
        else:
            return None

    @property
    def full_name(self):
        return "{} {}".format(self.user.first_name, self.user.last_name).strip()

    @property
    def first_name(self):
        return self.user.first_name

    @first_name.setter
    def first_name(self, value):
        self.user.first_name = value

    @property
    def last_name(self):
        return self.user.last_name

    @last_name.setter
    def last_name(self, value):
        self.user.last_name = value


class ClientPicture(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    name = models.CharField(max_length=250, default="", blank=True)
    image = models.ImageField(upload_to='client-picture')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.url

    @property
    def image_url(self):
        return self.image.url


class GuideProfile(models.Model):
    def __str__(self):
        return str(self.id)
