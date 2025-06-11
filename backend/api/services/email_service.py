from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_email(subject, to_email, template_name, context=None):
    """
    Отправка email с HTML шаблоном
    :param subject: Тема письма
    :param to_email: Email получателя (или список)
    :param template_name: Путь к HTML шаблону
    :param context: Контекст для шаблона
    """
    if context is None:
        context = {}

    # Рендеринг HTML содержимого
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)  # Текстовая версия

    # Создание письма
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [to_email] if isinstance(to_email, str) else to_email
    )
    email.attach_alternative(html_content, "text/html")

    # Отправка
    email.send()
