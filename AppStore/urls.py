"""AppStore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

import app.views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', app.views.index, name='index'),
    path('home', app.views.home, name ='home'),
    path('logout', app.views.logout, name='logout'),
    path('register', app.views.create_account, name='register'),
    path('new_request', app.views.new_request, name='new_request'),
    path('voucher', app.views.voucher, name='voucher'),
    path('profile', app.views.profile, name='profile'),
    path('admin_home', app.views.admin_home, name='admin_home'),
    path('admin_useredit/<str:email>', app.views.admin_useredit, name='admin_useredit'),
    path('admin_userview/<str:email>', app.views.admin_userview, name='admin_userview'),
    path('admin_voucher', app.views.admin_voucher, name='admin_voucher'),
    path('add', app.views.add_Original, name='add'),
    path('view/<str:id>', app.views.view_Original, name='view'),
    path('edit/<str:id>', app.views.edit_original, name='edit')
]
