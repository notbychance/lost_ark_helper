from celery import shared_task
from services.email_service import send_email


@shared_task(bind=True, max_retries=3)
def send_email_async(subject, to_email, template_name, context=None):
    send_email(subject, to_email, template_name, context)


@shared_task(bind=True, max_retries=3)
def send_invitation_email(to_email, invitation):
    context = {
        'registration_link': f'https://yourdomain.com/register?token={invitation}',
    }
    send_email(
        "Приглашение в систему Lost Ark Helper",
        to_email,
        "emails/invitation.html",
        context
    )
