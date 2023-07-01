from datetime import datetime
import random
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
import os
from django.utils.safestring import mark_safe

# Model classes
class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = models.TextField(verbose_name='Содержание')
    image = models.ImageField(null=True, blank=True, upload_to='images/articles/%Y/%m/%d', verbose_name='Изображение')
    created_at = models.DateField(blank=True, null=True, auto_now_add=True, verbose_name='Дата написания')

    def __str__(self):
        return f'Статья №{self.id}'

    class Meta:
        verbose_name = "Статью"
        verbose_name_plural = "Статьи"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Новость')
    text = models.TextField(verbose_name='Содержание')
    created_at = models.DateField(null=True, auto_now_add=True, verbose_name='Дата написания')

    def __str__(self):
        return f'Комментарий №{self.id} к статье №{self.article_id}'

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии к статьям"


class Advertisement(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    image = models.ImageField(upload_to='images/advertisements/%Y/%m/%d', verbose_name='Изображение')
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = models.TextField(verbose_name='Описание')
    price = models.IntegerField(verbose_name='Цена')
    is_close = models.BooleanField(default=False, verbose_name='Закрыто')
    created_at = models.DateField(null=True, auto_now_add=True, verbose_name='Дата написания')

    def __str__(self):
        return f'Объявление №{self.id}'

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"


class Car(models.Model):
    mark = models.CharField(max_length=200, verbose_name="Марка")
    model = models.CharField(max_length=200, verbose_name="Модель")
    year = models.IntegerField(verbose_name='Год выпуска')
    color = models.CharField(max_length=200, verbose_name="Цвет")
    vin_number = models.CharField(max_length=200, verbose_name="VIN номер")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, verbose_name='Объявление')

    def __str__(self):
        return f'Автомобиль №{self.id} из объявления №{self.advertisement_id}'

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"


class Rating(models.Model):
    evaluating = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluating', verbose_name='Оценивающий')
    evaluated = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluated', verbose_name='Оцениваемый')
    value = models.IntegerField(verbose_name='Оценка')

    class Meta:
       verbose_name = "Оценку"
       verbose_name_plural = "Оценки авторов объявлений"


class Сommunication(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender', verbose_name='Отправитель')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient', verbose_name='Получатель')
    text = models.TextField(verbose_name='Содержание')
    created_date = models.DateField(null=True, auto_now_add=True, verbose_name='Дата написания')
    created_time = models.TimeField(auto_now_add=True, null=True, verbose_name='Время написания')

    def __str__(self):
        return f'Сообщение пользователя №{self.sender_id} для пользователя №{self.recipient_id}'
    
    class Meta:
       verbose_name = "Сообщение"
       verbose_name_plural = "Общение"


# Inlines classes
class CommentInlines(admin.TabularInline):
    model = Comment
    fields = ['author', 'text']


# Admin classes
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'get_image')
    list_display_links = ('id', 'title')
    search_fields = ['title']
    readonly_fields = ['created_at']
    list_filter = ['created_at']
    date_hierarchy = "created_at"

    inlines = [CommentInlines]
    
    def get_image(self, object):
        return mark_safe(f'<img src="/static/{object.image}" width=70>')
    
    get_image.short_description = 'Изображение'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'article', 'created_at')
    list_display_links = ('id', 'author')
    search_fields = ['author__username', 'article__title']
    readonly_fields = ['created_at']
    list_filter = ['created_at']
    date_hierarchy = "created_at"


class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'price', 'is_close', 'created_at', 'get_image')
    list_display_links = ('id', 'author')
    search_fields = ['title', 'author__username']
    readonly_fields = ['created_at']
    list_filter = ['is_close', 'created_at']
    date_hierarchy = "created_at"

    def get_image(self, object):
        return mark_safe(f'<img src="/static/{object.image}" width=70>')
    
    get_image.short_description = 'Изображение'


class CarAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'advertisement', 'vin_number')
    list_display_links = ('id', 'owner')
    search_fields = ['advertisement__title', 'owner__username']


class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_info', 'value')
    list_display_links = ('id', 'get_info')
    search_fields = ['advertisement__title', 'owner__username']
    list_filter = ['value']

    def get_info(self, object):
        return f'Пользователь {object.evaluating.username} оценил пользователя {object.evaluated.username}'
    
    get_info.short_description = 'Информация'


class СommunicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_info', 'created_date', 'created_time')
    list_display_links = ('id', 'get_info')
    search_fields = ['sender__username', 'recipient__username']
    list_filter = ['created_date']
    readonly_fields = ['created_date', 'created_time']

    def get_info(self, object):
        return f'Пользователь {object.sender.username} написал пользователю {object.recipient.username}'
    
    get_info.short_description = 'Информация'