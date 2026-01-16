# Steam-like Android app (Kivy)

Коротко: это минимальное прототип-приложение на Python + Kivy для Android, демонстрирующее работу с аккаунтами Steam (локально) и создание mafile-файлов.

Установка зависимостей (в dev-окружении):

```bash
pip install -r requirements.txt
```

Запуск в десктоп-окружении:

```bash
python main.py
```

Описание:
- Главный экран показывает кнопку `Accounts :` и число аккаунтов.
- Страница `Accounts` содержит список аккаунтов (до 70% высоты), 4 элемента на странице.
- Каждый элемент открывает страницу аккаунта с кнопками `Delete`, `Edit`, `Confirmations`.
- Добавление аккаунта вручную: ввод `account_name`, `password`, `shared_secret`. При добавлении создаётся mafile в папке `mafiles/` и сохраняется в базе данных `accounts.db`.

mafile:
Файл создаётся в формате JSON (fallback) с полями `account_name`, `shared_secret`, `identity_secret`, `serial_number`, `revocation_code`, `time_created`, `uri`.
Если установлен пакет `steamguard` и в нём есть утилита для генерации mafile-байтов, код попробует её использовать.

Примечания:
- Этот репозиторий — прототип. Для реальной поддержки подтверждений Steam требуется корректная реализация через `steamguard` и сетевые вызовы, а также безопасное хранение секретов.
- Для сборки на Android используйте `buildozer` или `python-for-android`.
