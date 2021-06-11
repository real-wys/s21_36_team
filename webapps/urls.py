"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from project import views
from project.views import ChatNoticeListView, ChatNoticeUpdateView
from django.urls import path, include
import notifications.urls
from django.contrib.auth.decorators import login_required

urlpatterns = [

    #user-related function
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
    path('login', views.loginAction, name='login'),
    path('logout', views.logoutAction, name='logout'),
    path('myprofile', views.get_myprofile, name='myprofile'),
    # path('profile', views.profile, name='profile'),
    path('other_profile/<int:id>', views.other_profile_action, name='other_profile'),
    path('picture/<int:id>', views.get_picture, name='picture'),
    path('edituser', views.edituser, name='edituser'),
    path('editlawyer', views.editlawyer, name='editlawyer'),
    path('changeedit', views.change_edit, name='changeedit'),
    # path('project/'),include('project.urls'),
    
    #qna functino
    path('qna', views.qna_stream, name='qna'),
    path('create_question', views.create_question, name='create_question'),
    path('delete_question/<int:question_id>', views.delete_question, name='delete_question'),
    path('submit_answer/<question_id>', views.submit_answer, name="submit_answer"),
    path('questionPage/<question_id>', views.questionPage, name='questionPage'),
    path('get-qna', views.get_qna_action, name='get_qna'),
    path('add-answer', views.add_answer_action, name='add_answer'),

    #search function
    path('search_keyword',views.search_keyword,name='search_keyword'),

    #lawyer list
    path('lawyer-list',views.lawyer_list,name='lawyer-list'),
    
    #chat functions
    path('chat/<int:pk>', views.start_chat, name ='chat'),
    path('chatcontact', views.get_chatcontact, name ='chatcontact'),
    path('create_chatmessage/<int:pk>', views.create_chatmessage_action, name='create_chatmessage'),
    path('chat/get-chat/<int:pk>', views.get_chat_action, name='get_chat'),
    path('chat/get-image/<int:id>', views.get_msg_image, name='get-image'),

    # general and blogging function
    path('homepage', views.homepage, name='homepage'),
    path('blog/', views.blog, name='blog'),
    path('categories', views.categories, name='categories'),
    path('create_article', views.create_article, name='create_article'),
    path('delete_article/<int:article_id>', views.delete_article, name='delete_article'),
    path('articlePage/<article_id>', views.articlePage, name='articlePage'),
    path('submit_comment/<article_id>', views.submit_comment, name="submit_comment"),
    path('getImg/<int:type>/<int:id>', views.getImg, name='getImg'),
    path('demo', views.demo, name='demo'),
    path('collect/<int:id>/<int:type>', views.collect, name='collect'),
    path('like/<int:id>/<int:type>', views.like, name='like'),
    path('dislike/<int:id>/<int:type>', views.dislike, name='dislike'),
    path('searchByTag/', views.searchByTag, name='searchByTag'),

    # notification function
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    # path('notice/', include('notice.urls', namespace='notice')),
    path('notice_list/', login_required(views.ChatNoticeListView.as_view()), name='notice_list'),
    path('update/', login_required(views.ChatNoticeUpdateView.as_view()), name='notice_update'),

    

]
