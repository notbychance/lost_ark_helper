import hashlib
from datetime import datetime
import secrets
import base64
import uuid

from django.core.exceptions import ValidationError
from ..models import Group

def generate_invite_code(group_name: str) -> str:
    # 1. Хеш группы (SHA-256 в Base64)
    group_hash = base64.b64encode(
        hashlib.sha256(group_name.encode()).digest()
    ).decode()[:12].replace("=", "@")
    
    # 2. Текущая дата в HEX + Unix-время
    date_hex = datetime.now().strftime("%d%m%Y%H%M%S").encode().hex().upper()
    unix_time = str(int(datetime.now().timestamp()))
    
    # 3. Случайный сегмент с спецсимволами
    random_part = "".join([
        secrets.choice("!@#$%^&*") if i % 3 == 0 
        else secrets.choice("0123456789ABCDEF") 
        for i in range(16)
    ])
    
    # 4. Контрольная сумма (CRC32 от всего)
    combined = f"{group_hash}{date_hex}{unix_time}{random_part}"
    checksum = hex(hashlib.blake2b(combined.encode()).digest()[-1])[2:].zfill(2)
    
    # 5. Собираем всё в одном стиле "СЕГМЕНТ:СЕГМЕНТ@СЕГМЕНТ#КОНТРОЛЬ"
    return (
        f"{group_hash}:"
        f"{date_hex[:8]}@"
        f"{unix_time[-4:]}-"
        f"{random_part}#"
        f"{checksum}"
    )
    
def generate_unique_name():
    for _ in range(3):  # 3 попытки
        name = f'group-{uuid.uuid4().hex[:8]}'
        if not Group.objects.filter(name=name).exists():
            return name
    raise ValidationError("Cannot generate unique group name")