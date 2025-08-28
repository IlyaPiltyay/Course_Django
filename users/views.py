from django.contrib.auth import get_user_model, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, TemplateView
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from mailings.models import Newsletter
from .forms import CustomUserCreationForm
from .mixin import BlockUserMixin

User = get_user_model()  # Получаем пользовательскую модель


class UserListView(BlockUserMixin, ListView):
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        # Вернуть всех пользователей
        return User.objects.all()


class BlockUserView(BlockUserMixin, View):
    def post(self, request, user_id):
        user = self.get_object(user_id)
        if user:
            user.is_active = False  # Блокируем пользователя
            user.save()
            messages.success(request, f'Пользователь {user.email} заблокирован.')
        else:
            messages.error(request, "Пользователь не найден.")
        return redirect('user_list')

    def get_object(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


# Представление регистрации
class RegisterView(FormView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()

        subject = 'Добро пожаловать на наш сайт!'
        message = f'Уважаемый пользователь,\n\nСпасибо за регистрацию на нашем сайте!'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])  # Отправка сообщения о регистрации

        return super().form_valid(form)


# Представление для входа
class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('mailings:home')

class CustomLogoutView(View):
    def post(self, request):
        logout(request)  # Выход пользователя
        messages.success(request, "Вы успешно вышли из системы.")  # Сообщение о выходе
        return redirect('login')