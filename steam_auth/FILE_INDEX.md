# 📑 Steam Auth Manager - File Index

## 🎯 Быстрая навигация

### 🚀 Начать здесь
1. **[QUICKSTART.md](QUICKSTART.md)** - 5 минут на старт
2. **[setup.sh](setup.sh)** (Linux/Mac) или **[setup.bat](setup.bat)** (Windows) - быстрая установка

### 📖 Документация
- **[README.md](README.md)** - основная документация
- **[INSTALL.md](INSTALL.md)** - полная инструкция установки
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - руководство разработчика
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - полная сводка проекта
- **[STATISTICS.md](STATISTICS.md)** - статистика проекта
- **[STRUCTURE.txt](STRUCTURE.txt)** - подробная структура
- **[COMMANDS.md](COMMANDS.md)** - справка команд

### 💻 Исходный код

#### Главный файл
- **[main.py](main.py)** - точка входа приложения (100 строк)

#### Пакет app/
- **[app/__init__.py](app/__init__.py)** - инициализация пакета
- **[app/database.py](app/database.py)** - работа с SQLite БД (340 строк)
- **[app/steam_guard.py](app/steam_guard.py)** - Steam Guard и mafiles (250 строк)
- **[app/steam_utils.py](app/steam_utils.py)** - утилиты для Steam (380 строк)
- **[app/encryption.py](app/encryption.py)** - шифрование паролей (200 строк)
- **[app/config.py](app/config.py)** - управление конфигурацией (250 строк)
- **[app/logger.py](app/logger.py)** - система логирования (150 строк)
- **[app/screens.py](app/screens.py)** - все экраны Kivy (1200+ строк)

#### Тесты и примеры
- **[tests.py](tests.py)** - модульные тесты (400 строк, 20+ тестов)
- **[example.py](example.py)** - примеры использования API (200 строк)

### ⚙️ Конфигурация
- **[config.ini](config.ini)** - конфигурация приложения
- **[requirements.txt](requirements.txt)** - зависимости Python
- **[buildozer.spec](buildozer.spec)** - конфиг Android сборки

### 📁 Папки (создаются автоматически)
- **mafiles/** - хранилище mafiles
- **backups/** - резервные копии БД
- **logs/** - логи приложения
- **data/** - данные приложения (accounts.db)

---

## 📊 Статистика файлов

| Файл | Строк | Тип | Описание |
|------|-------|-----|---------|
| main.py | 100 | Python | Точка входа |
| app/database.py | 340 | Python | БД |
| app/steam_guard.py | 250 | Python | Steam Guard |
| app/steam_utils.py | 380 | Python | Утилиты |
| app/encryption.py | 200 | Python | Криптография |
| app/config.py | 250 | Python | Конфигурация |
| app/logger.py | 150 | Python | Логирование |
| app/screens.py | 1200+ | Python | UI (9 экранов) |
| tests.py | 400 | Python | Тесты |
| example.py | 200 | Python | Примеры |
| README.md | 350 | Документация | Основное |
| INSTALL.md | 300 | Документация | Установка |
| DEVELOPER_GUIDE.md | 350 | Документация | Разработка |
| PROJECT_SUMMARY.md | 400 | Документация | Сводка |
| QUICKSTART.md | 200 | Документация | Быстрый старт |
| COMMANDS.md | 300 | Документация | Команды |
| STATISTICS.md | 250 | Документация | Статистика |
| STRUCTURE.txt | 400 | Документация | Структура |
| config.ini | 50 | Конфиг | Настройки |
| requirements.txt | 6 | Конфиг | Зависимости |
| buildozer.spec | 40 | Конфиг | Android сборка |
| setup.sh | 70 | Script | Linux/Mac |
| setup.bat | 70 | Script | Windows |

**Всего: ~6000+ строк кода и документации**

---

## 🗂️ Структура директорий

```
steam_auth/
├── 📄 Документация (7 файлов)
│   ├── README.md
│   ├── INSTALL.md
│   ├── DEVELOPER_GUIDE.md
│   ├── PROJECT_SUMMARY.md
│   ├── QUICKSTART.md
│   ├── COMMANDS.md
│   ├── STATISTICS.md
│   └── STRUCTURE.txt
│
├── 💻 Python код (11 файлов)
│   ├── main.py
│   ├── tests.py
│   ├── example.py
│   └── app/
│       ├── __init__.py
│       ├── database.py
│       ├── steam_guard.py
│       ├── steam_utils.py
│       ├── encryption.py
│       ├── config.py
│       ├── logger.py
│       └── screens.py
│
├── ⚙️ Конфигурация (4 файла)
│   ├── config.ini
│   ├── requirements.txt
│   ├── buildozer.spec
│   └── FILE_INDEX.md (этот файл)
│
├── 🚀 Scripts (2 файла)
│   ├── setup.sh (Linux/Mac)
│   └── setup.bat (Windows)
│
└── 📁 Автоматические папки (создаются при запуске)
    ├── mafiles/
    ├── backups/
    ├── logs/
    ├── data/
    └── __pycache__/
```

---

## 🎯 По назначению

### Для начинающих
1. **QUICKSTART.md** - начните отсюда
2. **setup.sh/setup.bat** - установка
3. **example.py** - примеры
4. **README.md** - основное

### Для пользователей
1. **INSTALL.md** - установка на вашу платформу
2. **COMMANDS.md** - основные команды
3. **README.md** - как использовать
4. **QUICKSTART.md** - первые шаги

### Для разработчиков
1. **DEVELOPER_GUIDE.md** - архитектура
2. **PROJECT_SUMMARY.md** - обзор функций
3. **STRUCTURE.txt** - файловая структура
4. **Исходный код** в `app/`
5. **tests.py** - примеры тестов

### Для DevOps/CI
1. **buildozer.spec** - Android сборка
2. **requirements.txt** - зависимости
3. **setup.sh/setup.bat** - установка
4. **STATISTICS.md** - метрики

---

## 📚 Как читать документацию

### Первый раз?
```
QUICKSTART.md → setup.sh/bat → README.md → использование
```

### Хочу установить?
```
INSTALL.md (выбрать платформу) → COMMANDS.md → пример.py
```

### Хочу разрабатывать?
```
DEVELOPER_GUIDE.md → PROJECT_SUMMARY.md → исходный код (app/) → tests.py
```

### Нужна справка?
```
COMMANDS.md → example.py → README.md (секция Help)
```

### Проблемы?
```
INSTALL.md (раздел Troubleshooting) → logs/steamauth.log → tests.py
```

---

## 🔗 Перекрестные ссылки

### Из QUICKSTART.md
- [README.md](README.md) - полная документация
- [INSTALL.md](INSTALL.md) - инструкции
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - разработка

### Из INSTALL.md
- [README.md](README.md) - описание
- [COMMANDS.md](COMMANDS.md) - команды
- [example.py](example.py) - примеры

### Из DEVELOPER_GUIDE.md
- [app/screens.py](app/screens.py) - UI код
- [app/database.py](app/database.py) - БД
- [tests.py](tests.py) - тесты

### Из README.md
- [INSTALL.md](INSTALL.md) - установка
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - функции
- [STRUCTURE.txt](STRUCTURE.txt) - структура

---

## ✅ Контрольный список

### Перед использованием
- [ ] Прочитайте QUICKSTART.md
- [ ] Запустите setup.sh или setup.bat
- [ ] Запустите python tests.py
- [ ] Запустите python main.py

### Перед разработкой
- [ ] Прочитайте DEVELOPER_GUIDE.md
- [ ] Посмотрите STRUCTURE.txt
- [ ] Изучите app/screens.py
- [ ] Запустите tests.py
- [ ] Прочитайте PROJECT_SUMMARY.md

### Перед деплоем
- [ ] Все тесты проходят
- [ ] Логирование работает
- [ ] Конфигурация правильная
- [ ] БД создается и работает
- [ ] Нет ошибок синтаксиса

### Перед релизом
- [ ] Вся документация обновлена
- [ ] Версия изменена в коде
- [ ] README отредактирован
- [ ] CHANGELOG создан
- [ ] Коммитит в git

---

## 📞 Поддержка

### Документация
- Локальная документация: все файлы .md в корне
- Примеры: [example.py](example.py)
- Тесты: [tests.py](tests.py)

### Справка
- Команды: [COMMANDS.md](COMMANDS.md)
- Установка: [INSTALL.md](INSTALL.md)
- Разработка: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

### Логи
- Файл логов: `logs/steamauth.log`
- Уровень логирования: в `config.ini`
- Просмотр: `tail -f logs/steamauth.log` (Linux/Mac)

---

## 📅 Версии и история

### Версия 1.0.0 (текущая)
- ✅ Основной функционал
- ✅ 9 экранов Kivy
- ✅ SQLite БД
- ✅ Steam Guard 2FA
- ✅ Шифрование AES-256
- ✅ 20+ тестов
- ✅ Полная документация
- ✅ Android поддержка (Buildozer)

### Версия 0.9.0 (beta)
- Предварительная версия

### Версия 2.0.0 (планы)
- Cloud sync
- Backup/restore
- Экспорт JSON
- Биометрия
- QR коды

---

## 🎓 Обучающие ресурсы

### В проекте
- [example.py](example.py) - примеры кода
- [tests.py](tests.py) - примеры тестов
- [app/screens.py](app/screens.py) - Kivy примеры
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - лучшие практики

### Внешние ресурсы
- [Kivy Documentation](https://kivy.org/doc/)
- [Python Docs](https://docs.python.org/3/)
- [SQLite Docs](https://www.sqlite.org/docs.html)
- [Buildozer Docs](https://buildozer.readthedocs.io/)

---

## 🏷️ Теги и категории

### По типу файла
- **Python** (`.py`): main.py, app/*.py, tests.py, example.py
- **Документация** (`.md`): README.md, INSTALL.md и т.д.
- **Конфиг** (`.ini`, `.spec`, `.txt`): config.ini, buildozer.spec, requirements.txt
- **Scripts** (`.sh`, `.bat`): setup.sh, setup.bat

### По назначению
- **Ядро приложения**: main.py, app/screens.py
- **Данные**: app/database.py
- **Криптография**: app/encryption.py
- **Steam интеграция**: app/steam_guard.py, app/steam_utils.py
- **Конфигурация**: app/config.py, config.ini
- **Логирование**: app/logger.py, logs/
- **Тестирование**: tests.py

### По сложности
- **Простые**: setup.sh, requirements.txt
- **Средние**: example.py, tests.py
- **Сложные**: app/screens.py, app/steam_utils.py
- **Критичные**: app/database.py, app/encryption.py

---

## 💾 Размеры файлов

```
main.py                    ~4 KB
app/database.py            ~12 KB
app/steam_guard.py         ~9 KB
app/steam_utils.py         ~14 KB
app/encryption.py          ~8 KB
app/config.py              ~9 KB
app/logger.py              ~6 KB
app/screens.py             ~42 KB  (самый большой)
tests.py                   ~15 KB
example.py                 ~8 KB
README.md                  ~13 KB
INSTALL.md                 ~12 KB
DEVELOPER_GUIDE.md         ~13 KB
PROJECT_SUMMARY.md         ~15 KB
QUICKSTART.md              ~8 KB
COMMANDS.md                ~12 KB
STATISTICS.md              ~10 KB
STRUCTURE.txt              ~15 KB
config.ini                 ~2 KB
buildozer.spec             ~1.5 KB
requirements.txt           ~0.2 KB
setup.sh                   ~2.5 KB
setup.bat                  ~2.5 KB
```

**Всего**: ~250 KB исходного кода и документации

---

**Последнее обновление**: 2026-01-15
**Версия**: 1.0.0
**Статус**: ✅ Полностью документировано
