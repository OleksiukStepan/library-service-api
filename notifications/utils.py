from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model


@sync_to_async
def remove_chat_id(chat_id: int) -> None:
    user = get_user_model().objects.filter(telegram_chat_id=chat_id).first()

    if user:
        user.telegram_chat_id = None
        user.save()


@sync_to_async
def get_admin_chat_ids() -> set:

    return set(
        get_user_model()
        .objects.filter(is_staff=True, telegram_chat_id__isnull=False)
        .values_list("telegram_chat_id", flat=True)
    )
