from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from . models import Room, Topic, Message
from . forms import RoomForm, TopicForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def loginPage(request):
   if request.user.is_authenticated:
      return redirect('home')
   if request.method=='POST':
      username=request.POST.get('username').lower()
      password=request.POST.get('password')
      try:
         user=User.objects.get(username=username)
      except:
         messages.error(request, 'User does not exist!!!')

      user=authenticate(request, username=username, password=password)
      if user is not None:
         login(request, user)
         return redirect('home')
      else:
         messages.error(request, 'Username and password does not matches!!!')
   context={}
   return render(request, "base/log.html",context)

def logoutUser(request):
   logout(request)
   return redirect('home')

def registerPage(request):
   form=UserCreationForm()
   if request.method=="POST":
      form=UserCreationForm(request.POST)
      if form.is_valid():
         user=form.save()
         user.save()
         login(request, user)
         return redirect('home')
      else:
         messages.error(request, "An error occured!!!")
   context={'form':form}
   return render(request, "base/reg.html", context)



def home(request):
   q=request.GET.get('q') if request.GET.get('q')!=None else ''
   rooms=Room.objects.filter(
      Q(topic__name__icontains=q) |
      Q(name__icontains=q) |
      Q(description__icontains=q)
   )
   room_count=rooms.count()
   room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))
   topics=Topic.objects.all()
   context={'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}
   return render(request, "base/home.html", context)

def room(request,pk):
   room=Room.objects.get(id=pk)
   topics=Topic.objects.all()
   roomMessage=room.message_set.all().order_by('-created')
   participants=room.participants.all()
   if request.method=="POST":
      message=Message.objects.create(
         user=request.user,
         room=room,
         body=request.POST.get('body')
      )
      room.participants.add(request.user)
      return redirect('room', pk=room.id)
   context={'room':room,'roomMessage':roomMessage, 'participants': participants,'topics':topics}
   return render(request, "base/room.html", context)


def profile(request,pk):
   user=User.objects.get(id=pk)
   rooms=user.room_set.all()
   roomMessage=user.message_set.all()
   topics=Topic.objects.all()
   context={'user':user,'rooms':rooms,'topics':topics,'room_messages':roomMessage}
   return render(request, "base/profile.html", context)

@login_required(login_url='login')
def create(request):
   form=RoomForm()
   if request.method=="POST":
      form=RoomForm(request.POST)
      if form.is_valid:
         room=form.save(commit=False)
         room.host=request.user
         room.save()
         return redirect('home')
   context={'form':form}
   return render(request, "base/room_form.html", context)

@login_required(login_url='login')
def adtopic(request):
   form=TopicForm
   if request.method=="POST":
      form=TopicForm(request.POST)
      if form.is_valid:
         room=form.save()
         room.save()
         return redirect('home')
   context={'form':form}
   return render(request, "base/adtopic.html", context)

@login_required(login_url='login')
def updateRoom(request,pk):
   room=Room.objects.get(id=pk)
   form=RoomForm(instance=room)
   if request.user!=room.host:
      return HttpResponse("You are not allow")
   if request.method=="POST":
      form=RoomForm(request.POST,instance=room)
      if form.is_valid:
         form.save()
         return redirect('home')
   context={'form':form}
   return render(request, "base/room_form.html", context)

@login_required(login_url='login')
def deleteRoom(request,pk):
   room=Room.objects.get(id=pk)
   if request.user!=room.host:
      return HttpResponse("You are not allow")
   if request.method=="POST":
      room.delete()
      return redirect('home')
   return render(request, "base/delete.html", {'obj':room})

@login_required(login_url='login')
def deleteMsg(request,pk):
   message=Message.objects.get(id=pk)
   if request.user!=message.user:
      return HttpResponse("You are not allow")
   if request.method=="POST":
      message.delete()
      return redirect('home')
   return render(request, "base/delete.html", {'obj':message})
