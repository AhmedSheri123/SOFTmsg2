from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from .forms import (AddUserServiceModelForm, PatientManagementHospital, SchoolManagementProfile)
from .models import (ServicesModel, UserServiceModel, ServicePaymentOrderModel)
from django.contrib import messages
from django.conf import settings
import json, requests
from .payment import addInvoice, getInvoice
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from paypal.standard.forms import PayPalPaymentsForm
from decimal import Decimal

# Create your views here.
PatientManagementURL = settings.PATIENT_MANAGEMENT_WEB_SERVER_URL
SchoolManagementURL = settings.SCHOOL_MANAGEMENT_WEB_SERVER_URL

PAYPAL_RECIVVER_EMAIL = settings.PAYPAL_RECIVVER_EMAIL

def Home(request):
    user = request.user
    user_services = UserServiceModel.objects.filter(user=user)
    orders = ServicePaymentOrderModel.objects.filter(user_service__user=user)
    active_user_services = user_services.filter(progress='4')
    copmlited_orders = orders.filter(progress='3')
    uncopmlited_orders = orders.exclude(progress='3')
    
    context = {
        'active_user_services': active_user_services.count(),
        'copmlited_orders': copmlited_orders.count(),
        'uncopmlited_orders': uncopmlited_orders.count(),
        'orders':orders
    }
    return render(request, 'dashboard/home.html', context)

def MyServices(request):
    user_services = UserServiceModel.objects.filter(user=request.user)
    return render(request, 'dashboard/services/MyServices.html', {'user_services':user_services})

def DeletePatientManagementService(request, id):
    user_services = UserServiceModel.objects.get(id=id)
    service_user_id = user_services.service_user_id
    if service_user_id:
        res = requests.get(f'{PatientManagementURL}/en/accounts/DeletePatientManagementAPI/{service_user_id}')
        if res.status_code == 200:
            data = res.json()
            if data.get('status'):
                user_services.delete()
    else:user_services.delete()
    return redirect('MyServices')


def DeleteSchoolManagementService(request, id):
    user_services = UserServiceModel.objects.get(id=id)
    service_user_id = user_services.service_user_id
    if service_user_id:
        res = requests.get(f'{SchoolManagementURL}/en/DeleteSchoolManagementAPI/{service_user_id}')

        if res.status_code == 200:
            data = res.json()
            if data.get('status'):
                user_services.delete()
    else:user_services.delete()
    return redirect('MyServices')

def DeleteService(request, id):
    user_services = UserServiceModel.objects.get(id=id)
    service_user_id = user_services.service_user_id
    selected_service = user_services.service.service
    if service_user_id:
        if selected_service == '1':
            return DeletePatientManagementService(request, id)
        elif selected_service == '2':
            return DeleteSchoolManagementService(request, id)

def ResetPasswordService(request, id):
    if request.method == 'POST':
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password == password2:
            data = {
                'password':password
            }
            user_services = UserServiceModel.objects.get(id=id)
            service_user_id = user_services.service_user_id
            selected_service = user_services.service.service


            if service_user_id:
                if selected_service == '1':
                    res = requests.post(f'{PatientManagementURL}/en/accounts/ResetPasswordAPI/{service_user_id}', data=data)
                elif selected_service == '2':
                    res = requests.post(f'{SchoolManagementURL}/en/ResetPasswordAPI/{service_user_id}', data=data)

                if res.status_code == 200:
                    data = res.json()
                    if data.get('status'):
                        messages.success(request, 'Password has been changed successfully')
                else:messages.error(request, 'error on trying connect to server please call support')
            else:messages.error(request, 'error on changing password please call support')
        else:messages.error(request, 'new password field and repeat new password field not same')
    return redirect('ViewService', id)

def UserServiceCreationProgress(request, id):
    user_service = UserServiceModel.objects.get(id=id)
    progress = user_service.progress
    if progress == '1': return redirect('AddService')
    elif progress == '2': return redirect('ServicePlans', id)
    elif progress == '3':
        if user_service.service.service == '1':
            return redirect('AddPatientManagementSettings', id)
        elif user_service.service.service == '2':
            return redirect('AddSchoolManagementSettings', id)
        
    elif progress == '4':
        return redirect('ViewService', id)
    return redirect('MyServices')

def AddService(request):
    service_info_url = reverse('GetServiceInfo')
    form = AddUserServiceModelForm()
    if request.method == 'POST':
        form = AddUserServiceModelForm(data=request.POST)
        if form.is_valid():
            user_service = form.save(commit=False)
            user_service.user = request.user
            user_service.progress = '2'
            user_service.save()

            return redirect('UserServiceCreationProgress', user_service.id)
    return render(request, 'dashboard/services/AddService.html', {'form':form, 'service_info_url':service_info_url})


def ServicePlans(request, id):
    user_service = UserServiceModel.objects.get(id=id)
    plans_data = []
    selected_service = user_service.service.service
    if selected_service == '1':
        res = requests.get(f'{PatientManagementURL}/en/accounts/GetSubscriptionsPlanInfoAPI')
        if res.status_code == 200:
            plans_data = res.json()

    elif selected_service == '2':
        res = requests.get(f'{SchoolManagementURL}/en/GetSubscriptionsPlanInfoAPI')
        if res.status_code == 200:
            plans_data = res.json()

    if request.method == 'POST':
        plan_scope = request.POST.get('plan_scope')
        service_id = request.POST.get('selected_service_id')
        
        subscription_data = {}
        for plan in plans_data:
            if str(plan.get('id')) == service_id:
                subscription_data = plan
                break
        price = None
        if plan_scope == '1':
            price = Decimal(plan['price']['monthly']['value'])
        elif plan_scope == '2':
            price = Decimal(plan['price']['yearly']['value'])

        order = ServicePaymentOrderModel.objects.create(user_service=user_service)
        order.title = subscription_data.get('title')
        order.subscription_id = service_id
        order.progress_paid_plan_scope = plan_scope
        order.save()
        if price <= 0:
            return EnableServiceSubscription(request, order.orderID)
        # user_service.progress_paid_plan_id = service_id
        # user_service.progress_paid_plan_scope = plan_scope
        # user_service.progress = '3'
        # user_service.save()
        return redirect('ServicePayment', order.orderID)

    return render(request, 'dashboard/services/ServicePlans.html', {'plans_data':plans_data, 'user_service':user_service})

def ServicePayment(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    subscription_id = order.subscription_id

    selected_service = order.user_service.service.service
    plans_data = []
    if selected_service == '1':
        res = requests.get(f'{PatientManagementURL}/en/accounts/GetSubscriptionsPlanInfoAPI?id={subscription_id}')
        if res.status_code == 200:
            plans_data = res.json()

    elif selected_service == '2':
        res = requests.get(f'{SchoolManagementURL}/en/GetSubscriptionsPlanInfoAPI?id={subscription_id}')
        if res.status_code == 200:
            plans_data = res.json()

    if plans_data:
        plan = plans_data[0]
        ser_title = plan.get('title')
        ser_disc = plan.get('subtitle')
        price = None
        if order.progress_paid_plan_scope == '1':
            price = plan['price']['monthly']['value']
        elif order.progress_paid_plan_scope == '2':
            price = plan['price']['yearly']['value']

        user = request.user
        userprofile = user.userprofile
        index_url = request.build_absolute_uri('/')
        index_url = index_url.rsplit('/', 1)[0]              
        cancelUrl= index_url + reverse('CancellingOrder', kwargs={'orderID': orderID})
        PayPalCallBackUrl= index_url + reverse('PaypalCheckPaymentProcess', kwargs={'secret': order.order_secret})
        # PayPal Payment
        paypal_dict = {
            "business": PAYPAL_RECIVVER_EMAIL,
            "amount": price,
            "item_name": ser_title,
            "invoice": orderID,
            "currency_code": 'USD',
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return": PayPalCallBackUrl,
            "cancel_return": cancelUrl,
            "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
        }
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)

        if request.method == 'POST':

            
            clientName = user.first_name + ' ' + user.last_name
            total_price_amount = price
            email = user.email
            phone = userprofile.phone_number
            callBackUrl= index_url + reverse('checkPaymentProcess', kwargs={'orderID': orderID})

            p_res = addInvoice(orderID, total_price_amount, email, phone, clientName, ser_title, ser_disc, callBackUrl, cancelUrl, 'USD')
            if p_res.get('success'):
                order.transactionNo = p_res.get('transactionNo')
                order.save()
                return HttpResponseRedirect(p_res.get('url'))

        return render(request, 'dashboard/services/payment/pay.html', {'plan':plan, 'price':price, 'paypal_form':paypal_form})

    return redirect('ServicePlans', order.user_service.id)

def UpgradeOrRenewServiceSubscription(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    user_service = UserServiceModel.objects.get(id=order.user_service.id)

    if user_service.service.service == '1':
        return PatientManagementRenewSubscription(request, orderID)
    elif user_service.service.service == '2':
        return SchoolManagementRenewSubscription(request, orderID)
    

def EnableServiceSubscription(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    user_service = UserServiceModel.objects.get(id=order.user_service.id)
    if user_service.progress != '4':
        user_service.service_subscription_id = order.subscription_id
        user_service.plan_scope = order.progress_paid_plan_scope
        user_service.progress = '3'
        order.progress = '3'
        
        user_service.save()
        order.save()
        return redirect('UserServiceCreationProgress', user_service.id)
    else:
        order.progress = '2'
        return redirect('UpgradeOrRenewServiceSubscription', orderID)

def checkPaymentProcess(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    r = getInvoice(order.transactionNo)
    if r.get('success'):
        if r.get('orderStatus') == 'Paid':
            return EnableServiceSubscription(request, order.id)
    return redirect('index')

def PaypalCheckPaymentProcess(request, secret):
    orders = ServicePaymentOrderModel.objects.filter(order_secret=secret)
    if orders.exists():
        order = orders.first()
        return EnableServiceSubscription(request, order.id)
    return redirect('index')

def PatientManagementRenewSubscription(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    user_service = UserServiceModel.objects.get(id=order.user_service.id)
    post_data = {}
    post_data['subscription_id'] = order.subscription_id
    post_data['subscription_scope'] = order.progress_paid_plan_scope

    res = requests.post(f'{PatientManagementURL}/en/accounts/RenewSubscription/{user_service.service_user_id}', data=post_data)

    if res.status_code == 200:
        res_data = res.json()
        if res_data.get('status'):
            user_service.service_subscription_id = order.subscription_id
            user_service.plan_scope = order.progress_paid_plan_scope
            order.progress = '3'
            user_service.save()
            order.save()
            messages.success(request, 'تم تجديد الاشتراك بنجاح')
            return redirect('UserServiceCreationProgress', user_service.id)
        else:
            error_msgs = res_data.get('msgs')
            if error_msgs:
                for msg in error_msgs:
                    messages.error(request, msg)
    return

def SchoolManagementRenewSubscription(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    user_service = UserServiceModel.objects.get(id=order.user_service.id)
    post_data = {}
    post_data['subscription_id'] = order.subscription_id
    post_data['subscription_scope'] = order.progress_paid_plan_scope

    res = requests.post(f'{SchoolManagementURL}/en/RenewSubscription/{user_service.service_user_id}', data=post_data)

    if res.status_code == 200:
        res_data = res.json()
        if res_data.get('status'):
            user_service.service_subscription_id = order.subscription_id
            user_service.plan_scope = order.progress_paid_plan_scope
            order.progress = '3'
            user_service.save()
            order.save()
            messages.success(request, 'تم تجديد الاشتراك بنجاح')
            return redirect('UserServiceCreationProgress', user_service.id)
        else:
            error_msgs = res_data.get('msgs')
            if error_msgs:
                for msg in error_msgs:
                    messages.error(request, msg)
    return

def AddPatientManagementSettings(request, id):
    user = request.user
    user_service = UserServiceModel.objects.get(id=id)
    
    form = PatientManagementHospital()
    form.initial['first_name'] = user.first_name
    form.initial['last_name'] = user.last_name
    form.initial['number'] = user.userprofile.phone_number

    if request.method == 'POST':
        form = PatientManagementHospital(data=request.POST)
        if form.is_valid():
            post_data = form.cleaned_data
            post_data['subscription_id'] = user_service.service_subscription_id
            post_data['subscription_scope'] = user_service.plan_scope

            res = requests.post(f'{PatientManagementURL}/en/accounts/AddHospitalsByAPI', data=post_data)
            if res.status_code == 200:
                res_data = res.json()
                if res_data.get('status'):
                    service_user_id = res_data.get('user_id')
                    user_service.service_user_id=service_user_id
                    user_service.progress = '4'
                    user_service.save()
                    return redirect('UserServiceCreationProgress', user_service.id)
                else:
                    error_msgs = res_data.get('msgs')
                    if error_msgs:
                        for msg in error_msgs:
                            messages.error(request, msg)
    return render(request, 'dashboard/services/AddServiceSettings/AddPatientManagementSettings.html', {'form':form})

def AddSchoolManagementSettings(request, id):
    user = request.user
    user_service = UserServiceModel.objects.get(id=id)
    
    form = SchoolManagementProfile()
    form.initial['first_name'] = user.first_name
    form.initial['last_name'] = user.last_name
    form.initial['number'] = user.userprofile.phone_number

    if request.method == 'POST':
        form = SchoolManagementProfile(data=request.POST)
        if form.is_valid():
            post_data = form.cleaned_data
            post_data['subscription_id'] = user_service.service_subscription_id
            post_data['subscription_scope'] = user_service.plan_scope

            res = requests.post(f'{SchoolManagementURL}/en/AddHospitalsByAPI', data=post_data)
            if res.status_code == 200:
                res_data = res.json()
                if res_data.get('status'):
                    service_user_id = res_data.get('user_id')
                    user_service.service_user_id=service_user_id
                    user_service.progress = '4'
                    user_service.save()
                    return redirect('UserServiceCreationProgress', user_service.id)
                else:
                    error_msgs = res_data.get('msgs')
                    if error_msgs:
                        for msg in error_msgs:
                            messages.error(request, msg)
    return render(request, 'dashboard/services/AddServiceSettings/AddSchoolManagementSettings.html', {'form':form})

def ViewPatientManagementService(request, id):
    user_service = UserServiceModel.objects.get(id=id)
    plans_data = []
    res = requests.get(f'{PatientManagementURL}/en/accounts/GetPatientManagementInfo/{user_service.service_user_id}')
    plans_res = requests.get(f'{PatientManagementURL}/en/accounts/GetSubscriptionsPlanInfoAPI?id={user_service.service_subscription_id}')
    if plans_res.status_code == 200:
        plans_data = plans_res.json()
    if res.status_code == 200:
        data = res.json()
        if data:
            data['user_service'] = user_service
            return render(request, 'dashboard/services/viewService/ViewPatientManagementService.html', {'data':data, 'plans_data':plans_data, 'PatientManagementURL':PatientManagementURL})
    return redirect('MyServices')


def ViewSchoolManagementService(request, id):
    user_service = UserServiceModel.objects.get(id=id)
    plans_data = []
    res = requests.get(f'{SchoolManagementURL}/en/GetSchoolManagementInfo/{user_service.service_user_id}')
    plans_res = requests.get(f'{SchoolManagementURL}/en/GetSubscriptionsPlanInfoAPI?id={user_service.service_subscription_id}')
    if plans_res.status_code == 200:
        plans_data = plans_res.json()
    if res.status_code == 200:
        data = res.json()
        if data:
            data['user_service'] = user_service
            return render(request, 'dashboard/services/viewService/ViewSchoolManagementService.html', {'data':data, 'plans_data':plans_data, 'SchoolManagementURL':SchoolManagementURL})
    return redirect('MyServices')


def ViewService(request, id):
    
    user_service = UserServiceModel.objects.get(id=id)
    if user_service.service.service == '1':
        return ViewPatientManagementService(request, id)
    elif user_service.service.service == '2':
        return ViewSchoolManagementService(request, id)

def GetServiceInfo(request):
    id = request.GET.get('id')
    if id:
        service = ServicesModel.objects.get(id=id)
        data = {
            'status':True,
            'id':service.id,
            'title':service.title,
            'subtitle':service.sub_title,
        }
        return JsonResponse(data, safe=False)
    return JsonResponse({'status':False}, safe=False)



def MyOrders(request):
    orders = ServicePaymentOrderModel.objects.filter(user_service__user=request.user).order_by('-id')
    return render(request, 'dashboard/orders/MyOrders.html', {'orders':orders})

def DeleteOrder(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    order.delete()
    return redirect('MyOrders')

def CancellingOrder(request, orderID):
    order = ServicePaymentOrderModel.objects.get(orderID=orderID)
    order.progress = '4'
    order.save()
    return redirect('ServicePlans', order.user_service.id)