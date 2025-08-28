from django.db import models
from django.conf import settings


class Subscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name='Почта')
    full_name = models.CharField(max_length=255, verbose_name='Имя Получателя')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')

    def __str__(self):
        return self.full_name


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Сообщение')

    def __str__(self):
        return self.subject


class Newsletter(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('running', 'Запущена'),
        ('finished', 'Завершена'),
    ]

    scheduled_start = models.DateTimeField(null=True, blank=True, verbose_name='Время первой отправки')
    scheduled_end = models.DateTimeField(null=True, blank=True, verbose_name='Время окончания отправки')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='Статус ')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение')
    subscribers = models.ManyToManyField(Subscriber, verbose_name='Получатели ')
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    class Meta:
        permissions = [
            ('disable_newsletter', 'Can disable newsletters'),
        ]

    def __str__(self):
        return f"Рассылка {self.id}: {self.get_status_display()}"

    def start_sending(self):
        """ Метод для запуска рассылки. """
        self.status = 'running'
        self.save()

    def finish_sending(self):
        """ Метод для завершения рассылки. """
        self.status = 'finished'
        self.save()


class SendingAttempt(models.Model):
    STATUS_CHOICES = [
        ('successful', 'Успешно'),
        ('failed', 'Не успешно'),

    ]
    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    server_response = models.TextField()
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)

    def __str__(self):
        return f"Попытка для Рассылки {self.newsletter.id} на {self.attempt_time}"


