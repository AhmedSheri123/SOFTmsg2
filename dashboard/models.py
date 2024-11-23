from django.db import models
from django.contrib.auth.models import User
import random, string, datetime
# Create your models here.

def payOrderCodeGen(N = 4):
    res = ''.join(random.choices(string.digits, k=N))
    order = ServicePaymentOrderModel.objects.filter(orderID=res)
    if order.exists():
        res = payOrderCodeGen(N+1)
    return 'o' + str(res)
def payOrderSecretCodeGen():
    N = 99
    res = ''.join(random.choices((string.digits+string.ascii_letters), k=N))
    return str(res)

services_choices = [
    ('1', 'Patient Management'),
    ('2', 'School Management')
]

plan_scope_choices = [
    ('1', 'Monthly'),
    ('2', 'Yearly')
]

order_progress_choices = [
    ('1', 'Pending'),
    ('2', 'Paid'),
    ('3', 'Complited'),
    ('4', 'Cancelled')
]

user_service_progress_choices = [
    ('1', 'Create Project'),
    ('2', 'Choose Plan'),
    ('3', 'Project Settings'),
    ('4', 'Complited'),
]

class ServicesModel(models.Model):
    title = models.CharField(max_length=254)
    sub_title = models.TextField()
    service = models.CharField(max_length=254, choices=services_choices)

    creation_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)

class UserServiceModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    project_name = models.CharField(max_length=254, null=True)
    service = models.ForeignKey(ServicesModel, on_delete=models.CASCADE, null=True)
    progress = models.CharField(max_length=254, choices=user_service_progress_choices, null=True)

    service_subscription_id = models.CharField(max_length=254, null=True)
    service_user_id = models.CharField(max_length=254, null=True)
    service_subscription_date = models.CharField(max_length=254, null=True)
    plan_scope = models.CharField(max_length=254, choices=plan_scope_choices,  null=True)

    creation_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.project_name)

    @property
    def remaining_subscription(self):
        subscription_date = self.service_subscription_date
        if subscription_date:
            subscription_days = 30 if self.plan_scope else 365

            subscription_end_date = (datetime.timedelta(days=subscription_days) + subscription_date) - subscription_date
            print(subscription_end_date)

class ServicePaymentOrderModel(models.Model):
    user_service = models.ForeignKey(UserServiceModel, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=250, null=True, verbose_name="الاسم الثلاثي")
    subscription_id = models.CharField(max_length=254, null=True)
    progress_paid_plan_scope = models.CharField(max_length=254, choices=plan_scope_choices,  null=True)
    orderID = models.CharField(max_length=250, default=payOrderCodeGen, null=True, verbose_name="الاسم الثلاثي")
    order_secret = models.CharField(max_length=254, default=payOrderSecretCodeGen, null=True)
    transactionNo = models.CharField(max_length=250, null=True)
    progress = models.CharField(max_length=254, default='1', choices=order_progress_choices,  null=True)
    creation_date = models.DateTimeField(null=True, verbose_name="تاريخ الانشاء")