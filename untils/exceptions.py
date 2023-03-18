from fastapi import HTTPException

user_already_exists = HTTPException(status_code=1, detail="Аккаунт с таким электронным адресом уже существует. Пожалуйста, используйте другой адрес электронной почты или войдите в свой существующий аккаунт.")
user_not_exists = HTTPException(status_code=2, detail='Пользователь с таким идентификатором не существует. Пожалуйста, проверьте идентификатор или создайте нового пользователя.')
user_invalid_password = HTTPException(status_code=3, detail='Вы ввели неверный пароль. Пожалуйста, попробуйте еще раз или сбросьте свой пароль.')
token_expired = HTTPException(status_code=4, detail='Срок действия предоставленного вами токена истек. Пожалуйста, обновите свой токен или войдите снова.')

permission_denied = HTTPException(status_code=403, detail='У вас нет разрешения на доступ к этому ресурсу. Пожалуйста, свяжитесь с администратором или обновите свой аккаунт.')
user_unauthorized = HTTPException(status_code=401, detail='Несанкционированный!')
quiz_not_exists = HTTPException(status_code=5, detail='Викторина с таким идентификатором не существует. Пожалуйста, проверьте идентификатор или создайте новую викторину.')
quiz_session_not_exists = HTTPException(status_code=6, detail='Сессия викторины с таким идентификатором не существует. Пожалуйста, проверьте идентификатор или начните новую сессию.')