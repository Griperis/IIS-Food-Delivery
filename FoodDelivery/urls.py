from django.urls import path
from django.conf.urls import url
from django.conf.urls import include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user/', views.user_profile, name='user_profile'),
    path('facility/<int:facility_id>', views.facility_detail, name='facility_detail'),
    path('driver/', views.driver, name='driver'),
    path('operator/', views.operator, name='operator'),
    path('custom_admin/', views.admin, name='custom_admin')
]


#Add Django site authentication urls (for login, logout, registration)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register', views.register, name="register"),
]

