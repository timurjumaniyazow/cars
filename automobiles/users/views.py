from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserCreationForm
from django.views import View
from django.shortcuts import HttpResponsePermanentRedirect
from django.urls import reverse


class RegisterView(View):
    ''' Класс для регистрации новых пользователей '''
    template_name = 'registration/register.html'

    def get(self, request):
        context = {
            'form': UserCreationForm()
        }

        return render(request, self.template_name, context)
    
    def post(self, request):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponsePermanentRedirect(reverse('mainApp:index'))
        else:
            return render(request, self.template_name, {'form': form})
