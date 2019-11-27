from django.urls import path
from django.conf.urls import url
from django.conf.urls import include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user/', views.user_profile, name='user_profile'),
    path('user/edit_user', views.edit_user, name='edit_user'),
    path('user/change_password', views.change_password, name='change_password'),
    path('facility/<int:facility_id>', views.facility_detail, name='facility_detail'),
    path('order/<int:order_id>', views.order_summary, name='order_summary'),
    path('driver/', views.driver, name='driver'),
    path('operator/', views.operator, name='operator'),
    path('custom_admin/', views.admin, name='custom_admin'),

    path('create_facility', views.create_facility, name='create_facility'),
    path('edit_facility', views.edit_facility, name='edit_facility'),
    path('delete_facility', views.delete_facility, name='delete_facility'),
]

# Authentication urls!
urlpatterns += [
    path('login', views.login_user, name="login"),
    path('logout', views.logout_user, name="logout"),
    path('register', views.register, name="register"),
]

