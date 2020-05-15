from django.contrib.auth import authenticate, login  # Django's inbuilt authentication methods
from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from chat.models import Message, UserProfile
from chat.serializers import MessageSerializer, UserSerializer
from chat import PreProcessing
import joblib
import numpy as np
import pandas as pd
import re
from chat.tokens import account_activation_token
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .forms import (
    RegistrationForm,
    EditProfileForm
)

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required

@csrf_exempt  # Make the view csrf exempt.

def register(request):
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('chat/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = RegistrationForm()
    args = {'form': form}
    return render(request, 'chat/register.html', args)


def view_profile(request, pk=None):
    if pk:
        user = User.objects.get(pk=pk)
    else:
        user = request.user
    args = {'user': user}
    return render(request, 'chat/profile.html', args)

def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('chat:view_profile'))
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'chat/edit_profile.html', args)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print(user)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'chat/chat.html', {})
        #return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')
# Users View
def user_list(request, pk=None):
    """
    List all users, an unique user or create a new one.
    """
    if request.method == 'GET':
        if pk:  # If PrimaryKey (id) of the user is specified in the url
            users = User.objects.filter(id=pk)  # Select only that particular user
        else:
            users = User.objects.all()  # Else get all user list
            serializer = UserSerializer(users, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)  # Return serialized data

model = joblib.load('chat/Emo_model.pkl')  
vectorizer = joblib.load('chat/Emo_vect.pkl')
label=joblib.load('chat/Emo_label.pkl')
  
# Message view
@csrf_exempt
def message_list(request, sender=None, receiver=None):
    if request.method == 'GET':
        messages = Message.objects.filter(sender_id=sender, receiver_id=receiver, is_read=False)
        print(messages)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        for message in messages:
            message.is_read = True
            message.save()
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        x=str(data['message'])
        x = vectorizer.transform([x])
        data['sentiment']=' '.join(map(str,label.classes_[model.predict(x)]))
        serializer = MessageSerializer(data=data)
       
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

# Login page
def index(request):
    if request.user.is_authenticated:  # If the user is authenticated then redirect to the chat console
        return redirect('chat:chats')
    if request.method == 'GET':
        return render(request, 'chat/index.html', {})
    if request.method == "POST":  # Authentication of user
        username, password = request.POST['username'], request.POST['password']  # Retrieving username and password from the POST data.
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            return HttpResponse('{"error": "User does not exist"}')
        return redirect('chat:chats')

# View for listing the users
def chat_view(request):
    """
    Render the template with required context variables
    """
    if not request.user.is_authenticated:
        return redirect('chat:index')
    if request.method == "GET":
        return render(request, 'chat/chat.html',
                      {'users': User.objects.exclude(
                          username=request.user.username)})  # Returning context for all users except the current logged-in user

# View to render template for sending and receiving messages
# Takes arguments 'sender' and 'receiver' to identify the message list to return
def message_view(request, sender, receiver):
    """
    Render the template with required context variables
    """
    if not request.user.is_authenticated:
        return redirect('chat:index')
    if request.method == "GET":
        return render(request, "chat/messages.html",
                      {'users': User.objects.exclude(username=request.user.username),  # List of users
                       'receiver': User.objects.get(id=receiver),  # Receiver context user object for using in template
                       'messages': Message.objects.filter(sender_id=sender, receiver_id=receiver) | Message.objects.filter(sender_id=receiver,receiver_id=sender),
                       'sentiment': Message.objects.filter(sender_id=sender, receiver_id=receiver) |Message.objects.filter(sender_id=receiver,receiver_id=sender)})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect(reverse('chat:index'))
        else:
            return redirect(reverse('chat:change_password'))
    else:
        form = PasswordChangeForm(user=request.user)

        args = {'form': form}
        return render(request, 'chat/change_password.html', args)