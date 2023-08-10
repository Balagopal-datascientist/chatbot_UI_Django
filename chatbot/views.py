from django.shortcuts import render,redirect
from django.http import JsonResponse
from websockets import connect
import json
import asyncio
from django.contrib import auth
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
import os
from .models import Chat
from django.utils import timezone
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
# ws.connect("ws://0.0.0.0:9000/ws")
# Create your views here.
async def chatbot(request):
    async with connect("ws://localhost:9000/ws") as websocket:
        chats=Chat.objects.filter(user=request.user)
        if request.method == 'POST':
            message = request.POST.get('message')
            
            await websocket.send(json.dumps({
            "id": "hello world",
            "message": message}))
            resp= await asyncio.wait_for(websocket.recv(), timeout=1000000000)
            response=json.loads(resp)["text"]
            chat=Chat(user=request.user,message=message,response=response,created_at=timezone.now())
            chat.save()
            return JsonResponse({'message':message, 'response':response})
    return render(request,"chatbot.html",{'chats':chats})



def login(request):
    if request.method=='POST':
        username= request.POST['username']
        password=request.POST["password"]
        user=auth.authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('chatbot')
        else:
            error_message="invalid user "
            return render(request,'login.html',{"error_message":error_message})
    else:
        return render(request,'login.html')



def register(request):
    if request.method=='POST':
        username= request.POST['username']
        email=request.POST["email"]
        password1=request.POST["password1"]
        password2=request.POST['password2']
        if password1 == password2:
            try:
                user = User.objects.create_user(username,email,password1)
                user.save()
                auth.login(request,user)
                return redirect('chatbot')
            except Exception as e:
                error_message=f"{e}error creating account"
                return render(request,'register.html',{"error_message":error_message})
        else:
            error_message="passwords do not match"
        return render(request,'register.html',{"error_message":error_message})
    return render(request,"register.html")
def logout(request):
    auth.logout(request)
    return redirect('login')