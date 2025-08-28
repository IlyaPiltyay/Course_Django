from django.core.mail import send_mail
from django.conf import settings

from .models import SendingAttempt


def send_newsletter(newsletter, recipient):
    try:
        # Отправка электронной почты
        send_mail(
            newsletter.message.subject,
            newsletter.message.body,
            settings.EMAIL_HOST_USER,  # Укажите настоящий адрес отправителя
            [recipient],
        )

        # Успешная попытка отправки - создаем запись
        SendingAttempt.objects.create(
            status='successful',
            server_response='Email sent successfully',
            newsletter=newsletter,

        )

    except Exception as e:
        # Неуспешная попытка отправки - создаем запись
        SendingAttempt.objects.create(
            status='failed',
            server_response=str(e),
            newsletter=newsletter,

        )
