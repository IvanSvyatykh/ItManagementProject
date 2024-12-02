## Описание установки и запуска ngrok
- Установить ngrok `sudo apt install ngrok`
- Добавить токены для ngrok `ngrok config add-authtoken 2p9Zz33k9ycs6Xl77yJ7Q6nzTg9_4HdkVWb3B3pM5Fvm37iwW`
- Запустить ngrok у себя на машине `ngrok http --url=loved-jolly-cub.ngrok-free.app 8080`

## Описание запуска бота 
- Создать в директории `src` файл `.env`
- Заполнить его по шаблону из файла `.env.example`
- Находясь в корне проекта запустить бота через файл `/src/bot.py`
- Находясь в корне проекта `docker compose up -d`
- Находясь в корне проекта для создания миграции бд `alembic upgrade head`. Если меняли auth db в env, то обновить `sqlalchemy.url` в `alembic.ini` на свою строку.   