"""
URL configuration for inspection_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.http import HttpResponseRedirect
from inspections import views

urlpatterns = [
    path('', lambda request: HttpResponseRedirect('login/')),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('step1/', views.step1, name='step1'),
    path('step1_cust/', views.step1_cust, name='step1_cust'),
    path('menu/', views.menu, name='menu'),
    path('menu_cust/', views.menu_cust, name='menu_cust'),
    path('step2/', views.step2, name='step2'),
    path('step2_cust/', views.step2_cust, name='step2_cust'),
    path('step3/', views.step3, name='step3'),
    path('step4/', views.step4, name='step4'),
    path('step5/', views.step5, name='step5'),
    path('step6/', views.step6, name='step6'),
    path('service/', views.service, name='service'),
    path('rate/', views.rate, name='rate'),
    path('contact/', views.contact, name='contact'),
    path('settings/', views.settings_view, name='settings'),
    path('save-api-key/', views.settings_view, name='save_api_key'),
    path('process-image/', views.process_image, name='process_image'),
    path('gemini_summarize_api/', views.gemini_summarize_api, name='gemini_summarize_api'),
    path('gemini_process_issue/', views.gemini_process_issue, name='gemini_process_issue'),
    path('save/', views.save_signup_data, name='save_signup_data')
]
