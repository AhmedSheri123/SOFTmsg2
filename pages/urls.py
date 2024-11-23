from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('FAQ', views.FAQ, name='FAQ'),
    path('Contact', views.Contact, name='Contact'),
    path('SubscribeToUs', views.SubscribeToUs, name='SubscribeToUs'),
    path('Services/PatientManagement', views.PatientManagement, name='PatientManagement'),
    path('Services/SchoolManagement', views.SchoolManagement, name='SchoolManagement'),
    path('change_language/', views.change_language, name='change_language'),

]
