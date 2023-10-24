from django.urls import path
from app import views 


urlpatterns =[
    path('', views.home,name='home'),
    path('register',views.register,name='register'),
    path('login',views.logIn,name='login'),
    path('logout',views.logOut,name='logout'),
   # path('activate/<uidb64>/token', views.activate, name='activate')
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
              
              ]