"""
URL configuration for DjangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import include
from django.contrib import admin
from django.urls import path

from DjangoProject import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chats/create/', views.create_chat, name='create_chat'),
    path('chats/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('prompts/', views.prompt_list, name='prompt_list'),
    path('prompts/create/', views.create_prompt, name='create_prompt'),
    path('prompts/assign/', views.assign_prompt, name='assign_prompt'),
]
