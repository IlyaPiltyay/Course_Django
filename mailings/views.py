from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User

from django.shortcuts import redirect, render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, UpdateView, FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.urls import reverse
from django.core.cache import cache

from users.mixin import BlockUserMixin, ViewAllClientsMixin
from .mixins import DisableNewsletterMixin
from .models import Newsletter, SendingAttempt, Message, Subscriber
from .forms import NewsletterForm
from .services import send_newsletter


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Уникальный ключ кэша для статистики главной страницы
        cache_key = 'home_page_statistics'
        statistics = cache.get(cache_key)  # Пытаемся получить данные из кэша

        if statistics is None:
            # Если в кэше данных нет, получаем их из БД
            total_newsletters = Newsletter.objects.filter(is_active=False).count()
            active_newsletters = Newsletter.objects.filter(status='running', is_active=True).count()
            unique_recipients = Subscriber.objects.count()

            # Сохраняем данные в кэш
            statistics = {
                'total_newsletters': total_newsletters,
                'active_newsletters': active_newsletters,
                'unique_recipients': unique_recipients,
            }
            cache.set(cache_key, statistics, timeout=60 * 15)  # Кэшируем результаты на 15 минут

        # Обновляем контекст с данными из кэша
        context.update(statistics)
        return context


class NewsletterListView(ListView):
    model = Newsletter
    template_name = 'list.html'
    context_object_name = 'newsletters'

    def get_queryset(self):
        # Получаем данные напрямую из базы данных без кэширования
        return Newsletter.objects.filter(owner=self.request.user, is_active=True, status='created')

    def post(self, request, *args, **kwargs):
        newsletter_id = request.POST.get('newsletter_id')
        action = request.POST.get('action')

        try:
            newsletter = Newsletter.objects.get(id=newsletter_id)
            if action == "enable":
                newsletter.is_active = True
            elif action == "disable":
                newsletter.is_active = False
            newsletter.save()

            messages.success(request, 'Рассылка успешно обновлена.')
            return redirect('newsletter_list')
        except Newsletter.DoesNotExist:
            messages.error(request, 'Рассылка не найдена.')
            return redirect('newsletter_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class NewsletterCreateView(LoginRequiredMixin, FormView):
    form_class = NewsletterForm
    template_name = 'create.html'
    success_url = reverse_lazy('newsletter_list')

    def form_valid(self, form):
        user = form.instance.owner = self.request.user

        # Создаем и сохраняем объект Message
        message_instance = Message.objects.create(
            subject=form.cleaned_data['subject'],
            body=form.cleaned_data['body']
        )

        # Создаем и сохраняем объект Newsletter
        newsletter = Newsletter.objects.create(
            scheduled_start=form.cleaned_data['scheduled_start'],
            scheduled_end=form.cleaned_data['scheduled_end'],
            status='created',  # Установим статус в "Создана"
            message=message_instance,
            owner=user
        )  # Получаем список получателей и сохраняем их в Newsletter
        recipients = [email.strip() for email in form.cleaned_data['recipients'].replace(',', '\n').splitlines()]

        # Здесь нужно добавить логику для обработки получателей

        messages.success(self.request, 'Рассылка успешно создана.')
        return super().form_valid(form)


class NewsletterUpdateView(LoginRequiredMixin, UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'edit.html'
    success_url = '/newsletters/'  # Перенаправление по умолчанию (можно удалить)

    def form_valid(self, form):
        # Сначала сохраняем основной экземпляр Newsletter
        newsletter = form.save(commit=False)

        # Обновляем или создаем сообщение
        if form.cleaned_data['subject'] and form.cleaned_data['body']:
            message, created = Message.objects.get_or_create(
                subject=form.cleaned_data['subject'],
                body=form.cleaned_data['body']
            )
            newsletter.message = message  # Привязываем сообщение к рассылке

        # Обновляем время отправки и статус
        newsletter.status = form.cleaned_data.get('status', 'created')  # Обновление статуса, если требуется
        newsletter.save()  # Сохранение изменений

        # Обработка подписчиков
        recipient_emails = form.cleaned_data['recipients'].splitlines()
        newsletter.subscribers.clear()  # Очистка существующих подписчиков
        for email in recipient_emails:
            email = email.strip()
            if email:
                subscriber, _ = Subscriber.objects.get_or_create(email=email)
                newsletter.subscribers.add(subscriber)  # Добавление подписчика

        messages.success(self.request, "Рассылка успешно обновлена!")
        cache.clear()

        return super().form_valid(form)

    def get_success_url(self):
        # Перенаправление на список рассылок после обновления
        return reverse('newsletter_list')


class DeleteNewsletterView(LoginRequiredMixin, View):
    def post(self, request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk)

        # Проверяем права пользователя
        if newsletter.owner != request.user:
            messages.error(request, "У вас нет прав для удаления этой рассылки.")
            return redirect('newsletter_list')

        newsletter.delete()  # Физически удаляем рассылку
        messages.success(request, "Рассылка успешно удалена!")

        # Сбрасываем кэш главной страницы после удаления рассылки
        cache_key = 'home_page_statistics'
        cache.delete(cache_key)  # Удаляем кэш

        return redirect('newsletter_list')


class SendNewsletterView(View):
    def post(self, request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk)

        # Проверка статуса рассылки
        if newsletter.status == 'created':
            recipients = [subscriber.email for subscriber in newsletter.subscribers.all()]
            for recipient in recipients:
                # Отправка рассылки
                send_newsletter(newsletter, recipient)

            # Обновление статуса
            newsletter.status = 'running'  # Изменяем статус на "Запущена"
            newsletter.save()

            messages.success(request, 'Рассылка успешно отправлена!')
        else:
            messages.error(request, 'Рассылка не доступна для отправки (возможно, она уже завершена)!')

        return redirect('newsletter_list')


def statistics_view(request):
    successful_count = SendingAttempt.objects.filter(status='successful').count()
    failed_count = SendingAttempt.objects.filter(status='failed').count()
    total_attempts = successful_count + failed_count

    context = {
        'successful_count': successful_count,
        'failed_count': failed_count,
        'total_attempts': total_attempts,
    }
    return render(request, 'statistics.html', context)


User = get_user_model()


class ModeratorView(LoginRequiredMixin, UserPassesTestMixin,
                    DisableNewsletterMixin, BlockUserMixin, ViewAllClientsMixin, TemplateView):
    template_name = 'moderator.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = self.get_all_clients()  # Получаем всех пользователей
        context['newsletters'] = Newsletter.objects.all()  # Получаем все рассылки
        return context

    def get_all_clients(self):
        return User.objects.all()

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        newsletter_id = request.POST.get('newsletter_id')
        user_id = request.POST.get('user_id')  # Получаем ID пользователя для блокировки

        # Управление рассылками
        if newsletter_id:
            if action == 'disable':
                self.disable_newsletter(newsletter_id)  # Отключаем рассылку
            elif action == 'enable':
                self.enable_newsletter(newsletter_id)  # Включаем рассылку

        # Управление пользователями
        if user_id and action == 'block':
            self.block_user(user_id)  # Метод из BlockUserMixin

        return redirect('moderator')  # Перенаправляем обратно на панель модератора

    def test_func(self):
        # Проверка, состоит ли пользователь в группе 'Модераторы'
        return self.request.user.groups.filter(name='Manager').exists()
