from django import forms
from .models import Newsletter, Subscriber


class NewsletterForm(forms.ModelForm):
    subject = forms.CharField(max_length=255, required=True, label='Тема письма')
    body = forms.CharField(widget=forms.Textarea, required=True, label='Сообщение')
    recipients = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Введите email, каждый на новой строке'}),  # Подсказка в текстовом поле
        required=True,
        label='Кому отправить рассылку'
    )

    class Meta:
        model = Newsletter
        fields = ['scheduled_start', 'scheduled_end', 'subject', 'body', 'recipients']

    def save(self, commit=True):
        # Сохранение экземпляра Newsletter
        newsletter = super().save(commit=False)

        if commit:
            newsletter.save()  # Сначала сохраняем основные данные рассылки

        # Обработка полученных email-адресов
        recipient_emails = self.cleaned_data['recipients'].splitlines()
        for email in recipient_emails:
            email = email.strip()  # Удаляем лишние пробелы
            if email:
                subscriber, created = Subscriber.objects.get_or_create(email=email)
                newsletter.subscribers.add(subscriber)  # Добавляем подписчика к рассылке

        if commit:
            newsletter.save()

        return newsletter