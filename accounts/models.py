from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class ModelMixin(models.Model):
    """
        This mixins provide the default field in the models project wise
    """
    created_on = models.DateTimeField(auto_now=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_created",
                                   on_delete=models.CASCADE, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_updated",
                                   on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.created_by.email

    class Meta:
        abstract = True


class Otp(ModelMixin):
    OTP_VERIFY = (
        ('true', 'True'),
        ('false', 'False'),
    )
    OTP_TYPE = (
        ('register', 'register'),
        ('forgot', 'forgot'),
    )

    otp = models.IntegerField(default=0)
    type = models.CharField(max_length=20, choices=OTP_TYPE, default='forgot', null=True, blank=True)
    verify = models.CharField(choices=OTP_VERIFY, default='false', max_length=100)

class Country(models.Model):
    country_name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.country_name)
    
class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    state_name = models.CharField(max_length=30)

    def __str__(self):
        return "{} | {}".format(self.country.country_name, (self.state_name))
    
class Donation(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} | {}".format(self.title, (self.description))

class RequestDonation(ModelMixin):
    progress_type = (
        ('asked', 'asked'),
        ('received', 'received'),
    )
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    donation  = models.ForeignKey(Donation, null=True, blank=True, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.CASCADE)
    state = models.ForeignKey(State, null=True, blank=True, on_delete=models.CASCADE)
    end_date = models.DateTimeField(null=True, blank=True)
    progress_status = models.CharField(max_length=20, choices=progress_type, default='asked')

    