from email.message import EmailMessage
from uuid import uuid4

import aiosmtplib


class EmailManager:
    def __init__(self, username: str, password: str):
        self._smtp_client = aiosmtplib.SMTP(hostname="smtp.gmail.com", port=465, use_tls=True)
        self._username = username
        self._password = password

    async def init(self):
        await self._smtp_client.connect()
        await self._smtp_client.login(username=self._username, password=self._password)

    async def send_verify_url(self, email: str) -> str:
        token = uuid4()
        return str(token)

        message = self._new_message(email)
        url = f'http://213.226.125.145:8000/api/authorization/verify?token={token}'
        message.set_content(f'Авторитизация: {url}')
        message.add_alternative(f"<a href='{url}'>Авторитизоваться</a>", subtype='html')
        await self._smtp_client.send_message(message)
        return str(token)

    async def send_change_email(self, email: str) -> str:
        token = uuid4()
        return str(token)

        message = self._new_message(email)
        url = f'http://213.226.125.145:8000/api/authorization/verify_change_email?token={token}'
        message.set_content(f'Смена почты: {url}')
        message.add_alternative(f"<a href='{url}'>Смена почты</a>", subtype='html')
        await self._smtp_client.send_message(message)
        return str(token)

    def _new_message(self, email: str) -> EmailMessage:
        message = EmailMessage()
        message['From'] = self._username
        message['To'] = email
        return message
