from django.shortcuts import render , redirect
from django.contrib.auth.models import User , auth 
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from itertools import chain
import random
# Create your views here.

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)
    user_following_list = []
    feed = []
    profileobj =[]
    userobj =[]
    user_following = Followercount.objects.filter(follower = request.user.username)
    for users in user_following:
       user_following_list.append(users.user)
    for i in user_following_list:
       userobj_list = User.objects.filter(username = i)
       userobj.append(userobj_list)
    userobj_list = list(chain(*userobj))
    for i in userobj_list:
       newprof = Profile.objects.filter(user = i)
       profileobj.append(newprof)
    newprof = list(chain(*profileobj))
    for usernames in newprof:
       feed_list = Post.objects.filter(user = usernames)
       feed.append(feed_list)
    
    feed_list = list(chain(*feed))
    newfeed = sorted(feed_list,key=lambda post: post.created_at, reverse=True)
    all_users = User.objects.all()
    user_following_all = []
    for user in user_following:
       user_list = User.objects.get(username = user.user)
       user_following_all.append(user_list)

    new_suggestions_list = [ x for x in list(all_users) if ( x not in  list(user_following_all))]
    current_user = User.objects.filter(username = request.user.username)
    final_suggestions_list = [ x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    random.shuffle(final_suggestions_list)
    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
       username_profile.append(users.id)

    for ids in username_profile:
       profile_lists = Profile.objects.filter(id_user = ids)
       username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))
    context = {'user':user_profile,'post':newfeed ,'pro':profile ,'suggestions_username_profile_list':suggestions_username_profile_list[:4]}
    return render(request , 'index.html',context)



def signup(request):
    if request.method == 'POST':
       username = request.POST['username']
       email = request.POST['email']
       password1 = request.POST['password1']
       password2 = request.POST['password2']
       if password1 == password2:
          if User.objects.filter(email = email).exists():
             messages.info(request,'Email Taken')
             return redirect('signup')
          elif User.objects.filter(username = username).exists():
                messages.info(request,'Username Taken')
                return redirect('signup')
          else:
             user = User.objects.create_user(username=username , email=email , password=password1)
             user.save()
             user = authenticate(request, username=username, password=password1)
             login(request , user)
             user_model = User.objects.get(username = username)
             new_profile = Profile.objects.create(user = user_model , id_user= user_model.id)
             new_profile.save()
             messages.info(request , 'Finish setting up your profile')
             return redirect('settings')
       else:
          messages.info(request , 'Password Not Macthing')
          return redirect('signup')
    return render(request , 'signup.html')

def signin(request):
   if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
          auth.login(request, user)
          return redirect('index')
        else:
           messages.info(request , 'Password or Username Didnot Match')
           return redirect('signin')
   else:
    return render(request , 'signin.html')
   
@login_required(login_url='signin')
def logout(request):
   auth.logout(request)
   return redirect('signin')


@login_required(login_url='signin')
def settings(request):
   user_profile = Profile.objects.get(user = request.user)
   context = {'user':user_profile}
   if request.method == 'POST':
      if request.FILES.get('image') == None:
       image = user_profile.profileimg
       bio = request.POST['bio']
       location = request.POST['location']
       user_profile.profileimg = image
       user_profile.bio = bio
       user_profile.location = location
       user_profile.save()
      else:
       image = request.FILES.get('image')
       bio = request.POST['bio']
       location = request.POST['location']
       user_profile.profileimg = image
       user_profile.bio = bio
       user_profile.location = location
       user_profile.save()
      return redirect('/')
   else:
    
    return render(request , 'setting.html' , context)

@login_required(login_url='signin')
def profile(request,pk):
   user_object = User.objects.get(username = pk)
   user_profile = Profile.objects.get(user = user_object)
   pro_id = Profile.objects.get(id_user=user_profile.id_user)
   user_posts = Post.objects.filter(user = pro_id)
   user_post_length = len(user_posts)

   follower = request.user.username
   user = pk 
   if Followercount.objects.filter(follower = follower , user = user ).first():
      button_txt = 'Unfollow'
   else:
      button_txt = 'Follow'
   user_followers = len(Followercount.objects.filter(user = pk))
   user_following = len(Followercount.objects.filter(follower = pk))

   context = {
      'user_profile':user_profile,
      'user_object':user_object,
      'user_posts':user_posts,
      'user_post_length':user_post_length,
      'user_followers':user_followers,
      'button_txt':button_txt,
      'user_following':user_following
      }
   return render(request , 'profile.html',context)


def upload(request):
   if request.method == 'POST':
      user = User.objects.get(username=request.user.username)
      profile_user = Profile.objects.get(user=user)
      image = request.FILES.get('image_upload')
      caption = request.POST['caption']
      new_post = Post.objects.create(user=profile_user , image=image, caption=caption)
      new_post.save()
      return redirect('/')
   else:
    return redirect('/')

@login_required(login_url='signin')
def follow(request):
   if request.method == 'POST':
      follower = request.POST['follower']
      user = request.POST['user']
      if Followercount.objects.filter(follower= follower, user = user).first():
         delete_follower = Followercount.objects.get(follower= follower, user = user)
         delete_follower.delete()
         return redirect('/profile/'+user)
      else:
         newfollower = Followercount.objects.create(follower= follower, user = user)
         newfollower.save()
         return redirect('/profile/'+user)
   else:
      return redirect('/')
   

@login_required(login_url='signin')
def search(request):
   user_object = User.objects.get(username = request.user.username)
   user_profile = Profile.objects.get(user = user_object)
   if request.method == 'POST':
      username = request.POST['username']
      username_object = User.objects.filter(username__icontains = username)
      username_profile = []
      username_profile_list = []

      for users in username_object:
       username_profile.append(users.id)
      for ids in username_profile:
         profile_lists = Profile.objects.filter(id_user = ids)
         username_profile_list.append(profile_lists)

      username_profile_list = list(chain(*username_profile_list))
   return render(request,'search.html',{'user_profile':user_profile,'username_profile_list':username_profile_list})

@login_required(login_url='signin')
def message(request,pk):
   user = User.objects.get(username = request.user.username)
   receiver = User.objects.get(username = pk)
   if request.method == 'POST':
      sender = user
      receiver = receiver
      message = request.POST['text-msg']
      new_message= Message.objects.create(sender = sender , receiver = receiver , message = message)
      new_message.save()
   return render(request , 'message.html',{'receiver':receiver})
   
   