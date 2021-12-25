from django.urls import path
from . import views
#import LogoutView
from django.contrib.auth.views import LogoutView
app_name = 'handy'
urlpatterns = [
    path('register', views.CustomRegister.as_view(), name='register'),
    path('', views.IndexView.as_view(), name='index'),
    path('login', views.Login.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('services', views.ServiceListView.as_view(), name='services'),
    path('service', views.ServiceCreate.as_view(), name='service'),
    path('service/<int:pk>', views.ServiceDetail.as_view(), name='service-detail'),
    path('comment/<int:pk>', views.CommentCreate.as_view(), name='comment'),
    path('comment/<int:pk>/delete', views.CommentDelete.as_view(), name='comment-delete'),
    path('comment/<int:pk>/accept', views.CommentAccept.as_view(), name='comment-accept'),
    path('comment/<int:pk>/reject', views.CommentReject.as_view(), name='comment-reject'),
    path('complete/<int:service_pk>/<int:comment_pk>', views.complete_service, name='complete'),
    path('provider/<int:pk>', views.ProviderProfile.as_view(), name='provider-profile'),
]