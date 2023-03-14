from django.contrib import admin
from django.urls import path,include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from account import views 


admin.site.site_header = "GreenField Admin"
admin.site.site_title = "GreenField Admin Portal"
admin.site.index_title = "Welcome to GreenField admin Portal"

urlpatterns = [
    path('',views.home_page,name='home_page'),
    path('about_us',views.about_us,name='about_us'),
    # path('contact_us',views.contact_us,name='contact_us'),
    path('Login',views.Login,name='Login'),
    path('Logout',views.Logout,name='Logout'),
    path('SignUp',views.SignUp,name='SignUp'),
    path('pricing',views.pricing,name='pricing'),
    path('dashbord',views.dashbord, name='dashbord'),
    path('booking',views.booking, name='booking'),
    path('equipment',views.equipment, name='equiment'),
    path('verifyotp',views.verifyotp, name='verifyotp'),
    path('history',views.history, name='history'),
    path('all_bookings',views.all_bookings, name='all_bookings'),
    path('ratings',views.ratings, name='ratings'),
]

urlpatterns += staticfiles_urlpatterns()