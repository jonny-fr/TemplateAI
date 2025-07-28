from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from .models import Chat, Message, Prompt, UserPrompt
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
import requests

def index(request):
    return render(request, 'index.html')

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

@login_required
def chat_list(request):
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'chat_list.html', {'chats': chats})

@login_required
def chat_detail(request, chat_id):
    chat = Chat.objects.get(id=chat_id, user=request.user)
    messages = chat.messages.order_by('timestamp')
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Message.objects.create(chat=chat, sender='user', text=text, timestamp=timezone.now())
            # LM Studio API-Aufruf
            lm_messages = [
                {"role": "user" if m.sender == "user" else "assistant", "content": m.text}
                for m in chat.messages.order_by('timestamp')
            ]
            try:
                response = requests.post(
                    "http://localhost:1234/v1/chat/completions",
                    json={
                        "model": "local-model",  # Modellname kann ggf. angepasst werden
                        "messages": lm_messages,
                        "max_tokens": 512
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    ai_content = response.json()["choices"][0]["message"]["content"]
                else:
                    ai_content = f"[Fehler von LM Studio: {response.status_code}]"
            except Exception as e:
                ai_content = f"[LM Studio nicht erreichbar: {e}]"
            Message.objects.create(chat=chat, sender='ai', text=ai_content, timestamp=timezone.now())
        return HttpResponseRedirect(reverse('chat_detail', args=[chat.id]))
    return render(request, 'chat_detail.html', {'chat': chat, 'messages': messages})

@login_required
def create_chat(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            chat = Chat.objects.create(user=request.user, title=title)
            return redirect('chat_detail', chat_id=chat.id)
    return render(request, 'create_chat.html')

@login_required
def prompt_list(request):
    prompts = Prompt.objects.filter(creator=request.user)
    user_prompts = UserPrompt.objects.filter(user=request.user)
    return render(request, 'prompt_list.html', {'prompts': prompts, 'user_prompts': user_prompts})

@login_required
def create_prompt(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            Prompt.objects.create(creator=request.user, title=title, content=content)
            return redirect('prompt_list')
    return render(request, 'create_prompt.html')

@login_required
def assign_prompt(request):
    if request.method == 'POST':
        prompt_id = request.POST.get('prompt_id')
        try:
            prompt = Prompt.objects.get(id=prompt_id)
            UserPrompt.objects.get_or_create(user=request.user, prompt=prompt)
            return redirect('prompt_list')
        except Prompt.DoesNotExist:
            return render(request, 'assign_prompt.html', {'error': 'Prompt not found.'})
    return render(request, 'assign_prompt.html')
