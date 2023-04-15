from django.contrib import admin
from accounts.models import *
# Register your models here.

@admin.register(Otp)
class OTPModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'otp', 'type', 'verify')

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'country_name')

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'country', 'state_name')

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description')

@admin.register(RequestDonation)
class RequestDonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'donation', 'amount')

