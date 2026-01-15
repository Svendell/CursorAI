# Steam Auth Manager - Инструкция по установке

## Быстрый старт

### На Linux/Mac

```bash
# 1. Перейти в папку проекта
cd steam_auth

# 2. Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить приложение
python main.py
```

### На Windows

```bash
# 1. Перейти в папку проекта
cd steam_auth

# 2. Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить приложение
python main.py
```

## Установка для Android

### Требования

- Linux или Mac (Ubuntu 18.04+)
- Python 3.8+
- Java Development Kit (JDK) 11+
- Android SDK
- Android NDK (версия 25b)

### Установка Buildozer

```bash
# Установить buildozer
pip install buildozer

# На Ubuntu, установить зависимости
sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    openjdk-11-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    libffi-dev \
    libssl-dev \
    dos2unix \
    libc6-dev \
    m4 \
    graphviz \
    imagemagick \
    libreadline-gst-dev \
    libssl-dev \
    xsltproc \
    zip \
    openjdk-11-jdk \
    unzip \
    ant \
    ccache \
    libkxmlrpc3 \
    libxslt1-dev \
    libxml2-dev
```

### Сборка APK

```bash
# 1. Перейти в папку проекта
cd steam_auth

# 2. Инициализировать buildozer
buildozer android debug

# На первый запуск будут загружены Android SDK и NDK
# Это может занять 10-20 минут

# 3. APK файл будет создан в:
# bin/steamauth-1.0-debug.apk
```

### Установка APK на устройство

```bash
# Убедитесь, что устройство подключено по USB
adb devices

# Установить APK
adb install bin/steamauth-1.0-debug.apk

# Запустить приложение
adb shell am start -n org.steamauth.steamauth/.SteamAuthApp
```

## Примеры использования

### Запустить примеры кода

```bash
# Показать справку
python example.py help

# Добавить новый аккаунт
python example.py add

# Показать список аккаунтов
python example.py list

# Получить 2FA код
python example.py totp

# Создать mafile
python example.py create

# Импортировать mafile
python example.py import

# Валидировать mafile
python example.py validate

# Запустить все примеры
python example.py all
```

## Конфигурация

### Изменение размера окна

В файле `app/screens.py` измените:

```python
Window.size = (360, 800)  # Ширина x Высота пикселей
```

### Изменение папки для mafiles

В файле `app/steam_guard.py`:

```python
MAFILES_DIR = '/custom/path/to/mafiles'
```

## Структура базы данных

База данных автоматически создается при первом запуске (`accounts.db`).

### Таблица accounts

| Колонка | Тип | Описание |
|---------|-----|---------|
| id | INTEGER PRIMARY KEY | Уникальный ID |
| account_name | TEXT UNIQUE | Имя Steam аккаунта |
| password | TEXT | Пароль аккаунта |
| shared_secret | TEXT | Base64 shared secret для 2FA |
| identity_secret | TEXT | Base64 identity secret |
| revocation_code | TEXT | Код восстановления |
| created_at | TIMESTAMP | Дата создания |
| updated_at | TIMESTAMP | Дата обновления |

## Получение Shared Secret и Identity Secret

### Способ 1: Steam Desktop Authenticator

1. Откройте SDA
2. Перейдите в Settings
3. Нажмите "Show secrets"
4. Скопируйте Shared Secret и Identity Secret
5. Удалите SDA из настроек безопасности Steam
6. Используйте скопированные значения в приложении

### Способ 2: Экспорт из SDA

1. Найдите файл maFile (обычно в `~/.steam-authenticator/` или `~/.SDA/`)
2. Откройте JSON файл
3. Скопируйте значения `shared_secret` и `identity_secret`

### Способ 3: Вручную из Steam API

Это более сложный способ, требует использования Steam API и авторизации.

## Безопасность

### Важные примечания

1. **Пароли хранятся в открытом виде** по умолчанию
   - Используйте модуль `app/encryption.py` для шифрования
   - Следуйте примеру в `example.py`

2. **Используйте мастер пароль**
   - Установите мастер пароль при первом запуске
   - Все пароли будут шифроваться перед сохранением

3. **Резервное копирование**
   - Регулярно создавайте резервные копии `accounts.db`
   - Экспортируйте mafiles отдельно

### Шифрование паролей (пример)

```python
from app.encryption import SecureStorage

# Инициализировать хранилище с мастер паролем
storage = SecureStorage("my_master_password")

# Зашифровать пароль
encrypted = storage.encrypt_password("my_password")

# Расшифровать пароль
decrypted = storage.decrypt_password(encrypted)
```

## Решение проблем

### Проблема: ModuleNotFoundError при запуске

**Решение**: Убедитесь, что виртуальное окружение активировано:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Проблема: Ошибка при создании APK

**Решение**: Обновите buildozer:
```bash
pip install --upgrade buildozer
```

### Проблема: Киви не запускается на Mac

**Решение**: Установите дополнительные зависимости:
```bash
pip install kivy[full]
```

### Проблема: Нет доступа к файлам на Android

**Решение**: Добавьте права в `buildozer.spec`:
```
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
```

## Полезные ссылки

- [Kivy Documentation](https://kivy.org/doc/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Steam Guard Implementation](https://github.com/Jessecar96/SteamDesktopAuthenticator)
- [Python-steamguard](https://github.com/DoctorMcKay/node-steamcommunity)

## Поддержка

Если у вас возникают проблемы:

1. Проверьте, что установлены все зависимости
2. Убедитесь, что используется Python 3.8+
3. Прочитайте логи ошибок
4. Создайте issue в репозитории

## Лицензия

MIT
