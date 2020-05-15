from django.contrib.auth.views import LogoutView
from django.urls import path
from django.conf.urls import url
from . import views
from django.contrib.auth.views import (
    login, logout, password_reset, password_reset_done, password_reset_confirm,
    password_reset_complete
)

app_name='chat'
urlpatterns = [
    # WEB
    path('', views.index, name='index'),
    path('logout', LogoutView.as_view(next_page='chat:index'), name='logout') ,
    path('register/', views.register, name='register'),
    # URL to chat listing users
    path('chat', views.chat_view, name='chats'),
    # URL to see chat messages
    path('chat/<int:sender>/<int:receiver>', views.message_view, name='chat'),
    # URL to send and receive messages
    path('api/messages/<int:sender>/<int:receiver>', views.message_list, name='message-detail'),
    
    # API:
    # URL form : "/api/messages/1/2"
    path('api/messages/<int:sender>/<int:receiver>', views.message_list, name='message-detail'),  # For GET request.
    # URL form : "/api/messages/"
    path('api/messages/', views.message_list, name='message-list'),   # For POST
    # URL form "/api/users/1"
    path('api/users/<int:pk>', views.user_list, name='user-detail'),      # GET request for user with id
    # URL form "/api/users/"
    path('api/users/', views.user_list, name='user-list'),    # POST for new user and GET for all users list

    path('profile/', views.view_profile, name='view_profile'),
    url(r'^profile/(?P<pk>\d+)/$', views.view_profile, name='view_profile_with_pk'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('password/', views.change_password, name='change_password'),
    path('reset-password/', password_reset, {'template_name': 'chat/reset_password.html', 'post_reset_redirect': 'chat:password_reset_done', 'email_template_name': 'chat/reset_password_email.html'}, name='reset_password'),
    path('reset-password/done/', password_reset_done, {'template_name': 'chat/reset_password_done.html'}, name='password_reset_done'),
    url(r'^reset-password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',  password_reset_confirm, {'template_name': 'chat/reset_password_confirm.html', 'post_reset_redirect': 'chat:password_reset_complete'}, name='password_reset_confirm'),
    path('reset-password/complete/', password_reset_complete,{'template_name': 'chat/reset_password_complete.html'}, name='password_reset_complete'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate')
]