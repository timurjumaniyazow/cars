from django.shortcuts import render, get_object_or_404, HttpResponsePermanentRedirect
from django.urls import reverse
from .models import *
from django.http import JsonResponse
import json

# Create your views here.
def index(request):
    return render(request, 'index.html')

def error_404(request, exception):
    data = {
        'exception': exception
    }
    return render(request,'404.html', data)

def show_all_news(request):
    news = list(Article.objects.all())[::-1]
    return render(request, 'all_news.html', {'news': news})

def show_one_article(request, article_id:int):
    article = get_object_or_404(Article, pk=article_id)
    comments = Comment.objects.filter(article_id=article_id)

    return render(request, 'one_article.html', {'article': article, 'comments': comments})

def add_comment(request, article_id:int):
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated and get_object_or_404(Article, pk=article_id):
            comment = Comment()
            comment.article_id = article_id
            comment.author_id = user.id
            comment.text = request.POST.get('comment-text')
            comment.save()
            return HttpResponsePermanentRedirect(reverse('mainApp:one_article', kwargs={'article_id': article_id}))
        else:
            return render(request, 'error.html', {'error_title': 'Ошибка добавления', 
                                                  'error_text': 'Не удалось добавить комментарий'})
        

def delete_comment(request, comment_id:int):
    comment = get_object_or_404(Comment, pk=comment_id)
    article_id = comment.article_id
    user = request.user

    if user.is_authenticated and comment.author_id == user.id:
        comment.delete()
        return HttpResponsePermanentRedirect(reverse('mainApp:one_article', kwargs={'article_id': article_id}))
    return render(request, 'error.html', {'error_title': 'Ошибка удаления', 
                                                  'error_text': 'Вы не можете удалить комментарий другого человека'})


def show_all_advertisements(request):
    advertisements = list(Advertisement.objects.all())[::-1]

    return render(request, 'all_advertisements.html', {'advertisements': advertisements})

def show_one_advertisement(request, advertisement_id):
    advertisement = get_object_or_404(Advertisement, pk=advertisement_id)
    car = get_object_or_404(Car, advertisement_id=advertisement_id)
    author_rating = 0 + sum([record.value for record in Rating.objects.filter(evaluated_id=advertisement.author.id)])
    

    return render(request, 'one_advertisement.html', {'advertisement': advertisement, 'car': car, 'author_rating': author_rating})

def add_advertisement(request):
    if request.method == 'GET':
        return render(request, 'add_advertisement.html')
    elif request.method == 'POST':
        user = request.user
        title = request.POST.get('title')
        text = request.POST.get('text')
        price = request.POST.get('price')
        image = request.FILES['image']
        mark = request.POST.get('mark')
        model = request.POST.get('model')
        year = request.POST.get('year')
        color = request.POST.get('color')
        vin = request.POST.get('vin')
        
        new_advertisement = Advertisement()
        new_advertisement.author_id = user.id
        new_advertisement.image = image
        new_advertisement.title = title
        new_advertisement.text = text
        new_advertisement.price = price
        new_advertisement.is_close = False

        new_advertisement.save()

        new_car = Car()
        new_car.mark = mark
        new_car.model = model
        new_car.year = year
        new_car.color = color
        new_car.vin_number = vin
        new_car.owner_id = user.id
        new_car.advertisement_id = new_advertisement.id

        new_car.save()

        print(new_advertisement)
        print(new_car)

        return render(request, 'add_advertisement.html')
    
def delete_advertisement(request, advertisement_id:int):
        advertisement = get_object_or_404(Advertisement, pk=advertisement_id)
        user = request.user

        if user.is_authenticated and advertisement.author_id == user.id:
            advertisement.delete()
            return HttpResponsePermanentRedirect(reverse('mainApp:all_advertisements'))
        return render(request, 'error.html', {'error_title': 'Ошибка удаления', 
                                                    'error_text': 'Вы не можете удалить объявление другого человека'})

def show_author_profile(request, user_id:int):
    user = request.user

    author = get_object_or_404(User, pk=user_id)
    advertisements = list(Advertisement.objects.filter(author_id=user_id))[::-1]
    messages = []
    author_rating = 0 + sum([record.value for record in Rating.objects.filter(evaluated_id=author.id)])
    was_evaluated = ''

    context = {'author': author, 
               'advertisements': advertisements, 
               'messages': messages, 
               'author_rating': author_rating}

    if user.is_authenticated:
        if (user.id == author.id):
            messages = Сommunication.objects.filter(sender_id=user.id) | Сommunication.objects.filter(recipient_id=user.id)
            context['messages'] = sorted(messages, key=lambda x: (x.created_date, x.created_time), reverse=True)
        was_evaluated = list(Rating.objects.filter(evaluating_id=user.id, evaluated_id=author.id))
        if was_evaluated:
            context['was_evaluated'] = was_evaluated[0]
    return render(request, 'author_profile.html', context)


def to_chat(request, user_id:int):
    sender = request.user
    recipient = get_object_or_404(User, pk=user_id)
    messages = list(Сommunication.objects.filter(sender_id=sender.id, recipient_id=recipient.id) | Сommunication.objects.filter(sender_id=recipient.id, recipient_id=sender.id))
    messages = sorted(messages, key=lambda x: (x.created_date, x.created_time))

    if sender.is_authenticated:
        if sender.id != recipient.id:
            return render(request, 'chat.html', {'sender': sender, 'recipient': recipient, 'messages': messages})
    return render(request, 'error.html', {'error_title': 'Ошибка', 
                                                    'error_text': 'Что-то пошло не так'})


def send_message(request, user_id:int):
    sender = request.user
    recipient = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        new_message = Сommunication()
        new_message.sender = sender
        new_message.recipient = recipient
        new_message.text = request.POST.get('text')
        new_message.save()
    
    return HttpResponsePermanentRedirect(reverse('mainApp:chat', kwargs={'user_id': user_id}))
    

def set_rating(request):
    if request.method == 'GET':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            message = 'Это сообщение от сервера! У тебя получилось!'
            return JsonResponse({'message': message})
    if request.method == 'POST':
        message = ''
        data = json.loads(request.body)
        old_rating = Rating.objects.filter(evaluating_id=data['evaluating'], evaluated_id=data['evaluated'])

        if old_rating:
            old_rating.delete()
            message = data['action'] + ' delete'
        else:
            new_rating = Rating()
            new_rating.evaluating_id = data['evaluating']
            new_rating.evaluated_id = data['evaluated']
            new_rating.value = 1 if data['action'] == 'like' else -1
            message = data['action']
            new_rating.save()

        return JsonResponse({'message': message})