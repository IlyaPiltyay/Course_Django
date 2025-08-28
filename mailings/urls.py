from django.urls import path
from .views import NewsletterListView, NewsletterCreateView, NewsletterUpdateView, SendNewsletterView, HomePageView, \
    DeleteNewsletterView, statistics_view, ModeratorView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),  # главная страница
    path('list/', NewsletterListView.as_view(), name='newsletter_list'),  # Путь к списку рассылок
    path('create/', NewsletterCreateView.as_view(), name='create_newsletter'),  # Создание новой рассылки
    path('edit/<int:pk>/', NewsletterUpdateView.as_view(), name='edit_newsletter'),  # Редактирование рассылки
    path('send/<int:pk>/', SendNewsletterView.as_view(), name='send_newsletter_view'),  # Отправка рассылки
    path('delete/<int:pk>/', DeleteNewsletterView.as_view(), name='delete_newsletter'),  # Удаление рассылки
    path('statistics/', statistics_view, name='statistics_view'),  # Статистика
    path('moderator/', ModeratorView.as_view(), name='moderator'),  # Маршрут для модератора
]