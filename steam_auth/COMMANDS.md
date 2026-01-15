# Steam Auth Manager - Quick Commands Reference

## 🚀 Быстрый старт

### Linux/Mac
```bash
# Установка
chmod +x setup.sh
./setup.sh

# Запуск
source venv/bin/activate
python main.py
```

### Windows
```bash
# Установка
setup.bat

# Запуск
venv\Scripts\activate
python main.py
```

## 🎯 Основные команды

### Управление приложением

#### Запустить приложение
```bash
python main.py
```

#### Запустить примеры
```bash
python example.py help          # Показать справку
python example.py add           # Добавить аккаунт
python example.py list          # Список аккаунтов
python example.py totp          # Получить 2FA код
python example.py create        # Создать mafile
python example.py import        # Импортировать mafile
python example.py validate      # Валидировать mafile
python example.py all           # Все примеры
```

### Тестирование

#### Запустить все тесты
```bash
python tests.py
```

#### Запустить конкретный тест
```bash
python -m unittest tests.TestDatabase
python -m unittest tests.TestSteamGuard
python -m unittest tests.TestPasswordEncryption
```

### Конфигурация

#### Редактировать конфигурацию
```bash
# Linux/Mac
nano config.ini
# или
vim config.ini

# Windows
notepad config.ini
```

#### Просмотреть конфигурацию
```bash
cat config.ini          # Linux/Mac
type config.ini         # Windows
```

### Логирование

#### Просмотреть логи в реальном времени
```bash
# Linux/Mac
tail -f logs/steamauth.log

# Windows
type logs\steamauth.log
```

#### Очистить логи
```bash
# Linux/Mac
rm logs/steamauth.log
rm logs/steamauth.log.*

# Windows
del logs\steamauth.log
del logs\steamauth.log.*
```

### База данных

#### Резервная копия БД
```bash
# Linux/Mac
cp accounts.db backups/accounts_$(date +%Y-%m-%d_%H-%M-%S).db

# Windows
copy accounts.db backups\accounts_%date:~-4%%date:~-10,2%%date:~-7,2%.db
```

#### Удалить БД (будет пересоздана при запуске)
```bash
# Linux/Mac
rm accounts.db

# Windows
del accounts.db
```

#### Просмотреть содержимое БД
```bash
sqlite3 accounts.db
> SELECT * FROM accounts;
> .quit
```

### Mafiles

#### Просмотреть список mafiles
```bash
# Linux/Mac
ls -la mafiles/

# Windows
dir mafiles
```

#### Удалить mafile
```bash
# Linux/Mac
rm mafiles/account_name.maFile

# Windows
del mafiles\account_name.maFile
```

## 📦 Управление зависимостями

### Установить зависимости
```bash
pip install -r requirements.txt
```

### Обновить зависимости
```bash
pip install --upgrade -r requirements.txt
```

### Создать список зависимостей
```bash
pip freeze > requirements-lock.txt
```

### Удалить виртуальное окружение
```bash
# Linux/Mac
rm -rf venv

# Windows
rmdir /s venv
```

## 🔧 Разработка

### Форматирование кода (Black)
```bash
pip install black
black app/
```

### Статический анализ (Pylint)
```bash
pip install pylint
pylint app/*.py
```

### Проверка типов (Mypy)
```bash
pip install mypy
mypy app/
```

### Покрытие тестами (Coverage)
```bash
pip install coverage
coverage run -m unittest tests
coverage report
coverage html  # Создать HTML отчет
```

## 📱 Android разработка

### Установить Buildozer
```bash
pip install buildozer
```

### Инициализировать для Android
```bash
buildozer android debug
```

### Собрать APK
```bash
buildozer android debug    # Debug APK
buildozer android release  # Release APK (требует подписание)
```

### Установить на устройство
```bash
adb install bin/steamauth-1.0-debug.apk
```

### Переустановить приложение
```bash
adb install -r bin/steamauth-1.0-debug.apk
```

### Удалить приложение
```bash
adb uninstall org.steamauth.steamauth
```

### Просмотреть логи
```bash
adb logcat | grep python
```

### Запустить приложение
```bash
adb shell am start -n org.steamauth.steamauth/.SteamAuthApp
```

## 📝 Документация

### Просмотреть файлы

```bash
cat README.md           # Основная документация
cat INSTALL.md          # Инструкции установки
cat DEVELOPER_GUIDE.md  # Руководство разработчика
cat PROJECT_SUMMARY.md  # Сводка проекта
cat STRUCTURE.txt       # Структура проекта
```

## 🐛 Отладка

### Запустить с debug логированием
```bash
# Отредактируйте config.ini
# [LOGGING]
# log_level = 2  # Debug режим

python main.py
```

### Запустить Python интерпретатор
```bash
python
>>> from app.database import Database
>>> db = Database()
>>> accounts = db.get_all_accounts()
>>> print(accounts)
>>> exit()
```

### Очистить Python кеш
```bash
# Linux/Mac
find . -type d -name __pycache__ -exec rm -rf {} +

# Windows
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
```

## ⚙️ Git команды (если используется)

### Инициализировать репозиторий
```bash
git init
git add .
git commit -m "Initial commit"
```

### Создать новую ветку
```bash
git checkout -b feature/new-feature
```

### Проверить статус
```bash
git status
```

### Просмотреть изменения
```bash
git diff
```

### Коммитить изменения
```bash
git add .
git commit -m "Описание изменений"
```

### Опубликовать ветку
```bash
git push origin feature/new-feature
```

## 🔐 Безопасность

### Создать .gitignore
```bash
echo "venv/" >> .gitignore
echo "accounts.db" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.maFile" >> .gitignore
echo "logs/" >> .gitignore
echo "backups/" >> .gitignore
echo ".env" >> .gitignore
```

### Защитить конфиденциальные файлы
```bash
# Linux/Mac
chmod 600 config.ini
chmod 600 accounts.db

# Windows
icacls config.ini /grant:r %username%:F /inheritance:r
icacls accounts.db /grant:r %username%:F /inheritance:r
```

## 📊 Полезные утилиты

### Просмотреть размер файлов
```bash
# Linux/Mac
du -sh *

# Windows
dir /s
```

### Найти файлы по маске
```bash
# Linux/Mac
find . -name "*.py" -type f

# Windows
forfiles /S /M *.py
```

### Подсчитать строки кода
```bash
# Linux/Mac
find app -name "*.py" -exec wc -l {} + | tail -1

# Windows
(for /f "tokens=*" %f in ('dir /s /b app\*.py') do @type "%f") | find /c /v ""
```

## 🆘 Помощь

### Получить справку по команде
```bash
python main.py --help
python example.py help
python tests.py --help
```

### Просмотреть версию
```bash
python --version
python main.py --version (если реализовано)
```

### Сообщить об ошибке
1. Проверьте логи: `logs/steamauth.log`
2. Запустите тесты: `python tests.py`
3. Проверьте документацию в README.md
4. Создайте issue с описанием проблемы

---

**Версия**: 1.0.0
**Обновлено**: 2026-01-15

Для более подробной информации смотрите README.md, INSTALL.md и DEVELOPER_GUIDE.md
