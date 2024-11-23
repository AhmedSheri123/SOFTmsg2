from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='DashboardHome'),
    path('MyServices', views.MyServices, name='MyServices'),
    path('AddService', views.AddService, name='AddService'),
    path('DeleteService/<int:id>', views.DeleteService, name='DeleteService'),
    path('GetServiceInfo', views.GetServiceInfo, name='GetServiceInfo'),
    path('UserServiceCreationProgress/<int:id>', views.UserServiceCreationProgress, name='UserServiceCreationProgress'),
    path('AddPatientManagementSettings/<int:id>', views.AddPatientManagementSettings, name='AddPatientManagementSettings'),
    path('AddSchoolManagementSettings/<int:id>', views.AddSchoolManagementSettings, name='AddSchoolManagementSettings'),
    path('ResetPasswordService/<int:id>', views.ResetPasswordService, name='ResetPasswordService'),
    
    path('ServicePlans/<int:id>', views.ServicePlans, name='ServicePlans'),
    path('ServicePayment/<str:orderID>', views.ServicePayment, name='ServicePayment'),
    path('checkPaymentProcess/<str:orderID>', views.checkPaymentProcess, name='checkPaymentProcess'),
    path('PaypalCheckPaymentProcess/<str:secret>', views.PaypalCheckPaymentProcess, name='PaypalCheckPaymentProcess'),
    path('UpgradeOrRenewServiceSubscription/<str:orderID>', views.UpgradeOrRenewServiceSubscription, name='UpgradeOrRenewServiceSubscription'),
    path('EnableServiceSubscription/<str:orderID>', views.EnableServiceSubscription, name='EnableServiceSubscription'),
    path('ViewService/<int:id>', views.ViewService, name='ViewService'),
    path('ViewPatientManagementService/<int:id>', views.ViewPatientManagementService, name='ViewPatientManagementService'),
    path('MyOrders', views.MyOrders, name='MyOrders'),
    path('DeleteOrder/<str:orderID>', views.DeleteOrder, name='DeleteOrder'),
    path('CancellingOrder/<str:orderID>', views.CancellingOrder, name='CancellingOrder'),
]
