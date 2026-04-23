from django.db import models

from libs.choices import Choices
from libs.fields import ChoicesField, MoneyField


class Account(models.Model):
    balance = MoneyField(default=0.0)

    def __str__(self):
        return str(self.id)


class AccountReplenishment(models.Model):
    STATUSES = Choices(
        'created',
        'accepted',
        'declined',
    )

    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    amount = MoneyField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = ChoicesField(choices=STATUSES, default=STATUSES.created)
    reason = models.TextField(default="", blank=True)

    def __str__(self):
        return str(self.id)


class AccountWithdrawal(models.Model):
    STATUSES = Choices(
        'created',
        'accepted',
        'declined',
    )

    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    amount = MoneyField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = ChoicesField(choices=STATUSES, default=STATUSES.created)
    reason = models.TextField(default="", blank=True)

    def __str__(self):
        return str(self.id)


class AccountTransfer(models.Model):
    STATUSES = Choices(
        'created',
        'accepted',
        'declined',
    )

    account_from = models.ForeignKey('Account', on_delete=models.CASCADE,
                                     related_name='transfers_from')
    account_to = models.ForeignKey('Account', on_delete=models.CASCADE,
                                   related_name='transfers_to')
    trip = models.ForeignKey('Trip', on_delete=models.CASCADE)
    amount = MoneyField()
    created_at = models.DateTimeField(auto_now_add=True)
    performed_at = models.DateTimeField()
    status = ChoicesField(choices=STATUSES, default=STATUSES.created)
    reason = models.TextField(default="", blank=True)

    def __str__(self):
        return str(self.id)
