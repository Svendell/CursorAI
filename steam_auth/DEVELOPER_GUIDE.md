# Steam Auth Manager - Developer Guide

## 🏗️ Архитектура приложения

### MVC Паттерн (Model-View-Controller)

```
┌─────────────────────────────────────────┐
│         KIVY UI LAYER (screens.py)      │
│  (View - все экраны приложения)         │
└─────────────────────────────────────────┘
           ↓         ↑
┌─────────────────────────────────────────┐
│      BUSINESS LOGIC LAYER               │
│  ├─ steam_guard.py (Steam Guard)        │
│  ├─ steam_utils.py (Утилиты)            │
│  └─ encryption.py (Криптография)        │
└─────────────────────────────────────────┘
           ↓         ↑
┌─────────────────────────────────────────┐
│     DATA ACCESS LAYER                   │
│  ├─ database.py (SQLite)                │
│  └─ config.py (Configuration)           │
└─────────────────────────────────────────┘
```

## 🔄 Поток данных

```
User Input (UI) → Screen Handler → Business Logic → Database
                                  → Steam Guard
                                  → Encryption
                                  ↓
                            Return Data → Update UI
```

## 📝 Добавление нового экрана

### 1. Создать класс экрана в screens.py
```python
class NewScreen(Screen):
    def __init__(self, db: Database, **kwargs):
        super().__init__(**kwargs)
        self.db = db
    
    def on_enter(self):
        # Вызывается когда экран активируется
        self.build_ui()
    
    def build_ui(self):
        # Построить интерфейс
        layout = BoxLayout(orientation='vertical')
        # ... добавить элементы ...
        self.add_widget(layout)
```

### 2. Зарегистрировать экран в main.py
```python
self.root.add_widget(NewScreen(self.db, name='new_screen'))
```

### 3. Добавить навигацию
```python
# В другом экране
def go_to_new_screen(self, instance):
    self.manager.current = 'new_screen'
```

## 🔧 Добавление новой функции

### Пример: Добавить экспорт в JSON

#### 1. Создать метод в steam_guard.py
```python
def export_accounts_json(self, accounts: List[Dict]) -> str:
    """Экспортировать аккаунты в JSON"""
    json_data = json.dumps(accounts, indent=2)
    with open('export.json', 'w') as f:
        f.write(json_data)
    return 'export.json'
```

#### 2. Создать кнопку в UI (screens.py)
```python
export_btn = Button(text='Export JSON')
export_btn.bind(on_press=self.export_accounts)

def export_accounts(self, instance):
    accounts = self.db.get_all_accounts()
    path = self.guard_manager.export_accounts_json(accounts)
    # Показать сообщение об успехе
```

#### 3. Протестировать (tests.py)
```python
def test_export_json(self):
    # Добавить тест
```

## 📊 Диаграмма классов

```
Database
├── add_account()
├── get_account()
├── get_all_accounts()
├── update_account()
├── delete_account()
└── count_accounts()

SteamGuardManager
├── create_mafile_from_dict()
├── import_mafile()
├── get_steam_guard_code()
├── get_confirmation_operations()
└── confirm_operation()

PasswordEncryption
├── encrypt()
├── decrypt()
└── derive_key()

Config
├── get()
├── set()
├── get_int()
├── get_bool()
└── get_all()

Screen (Kivy)
├── HomeScreen
├── AccountsScreen
├── AccountScreen
├── EditAccountScreen
├── ConfirmationsScreen
├── AddAccountScreen
├── ManualAddScreen
├── CreateMafileScreen
└── ImportMafileScreen
```

## 🧪 Написание тестов

### Шаблон для нового теста
```python
class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Подготовка перед тестом"""
        self.db = Database(tempfile.NamedTemporaryFile().name)
    
    def tearDown(self):
        """Очистка после теста"""
        pass
    
    def test_something(self):
        """Тест какой-то функции"""
        result = some_function()
        self.assertEqual(result, expected_value)
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        with self.assertRaises(ValueError):
            bad_function()
```

## 🔍 Отладка

### Включить debug логирование
```ini
[LOGGING]
log_level = 2
```

### Просмотреть логи
```bash
tail -f logs/steamauth.log
```

### Использовать print для debug
```python
from app.logger import log_debug

log_debug(f"Variable value: {variable}")
```

### Запустить с verbose режимом
```bash
python main.py 2>&1 | grep -i debug
```

## 🚨 Обработка ошибок

### Правильный способ
```python
try:
    account_id = db.add_account(name, password, secret)
except ValueError as e:
    log_error(f"Ошибка добавления аккаунта: {e}")
    show_popup("Error", str(e))
except Exception as e:
    log_error(f"Неожиданная ошибка: {e}", e)
    show_popup("Error", "Something went wrong")
```

## 📚 Документирование кода

### Стиль документации (docstrings)
```python
def get_account(self, account_id: int) -> Optional[Dict[str, Any]]:
    """
    Получить аккаунт по ID
    
    Args:
        account_id: Уникальный идентификатор аккаунта
    
    Returns:
        Словарь с данными аккаунта или None если не найден
    
    Raises:
        ValueError: Если account_id некорректен
    
    Example:
        >>> db = Database()
        >>> account = db.get_account(1)
        >>> print(account['account_name'])
    """
```

## 🎨 Стиль кода

### PEP 8 требования
- Используйте 4 пробела для отступа
- Максимум 79 символов на строку
- Две пустые строки между функциями класса
- Импорты в начале файла

### Пример
```python
from typing import Dict, List, Optional

class MyClass:
    """Описание класса"""
    
    def __init__(self):
        """Инициализация"""
        self.value = None
    
    def method_one(self) -> str:
        """Первый метод"""
        return "result"
    
    def method_two(self, param: int) -> bool:
        """Второй метод"""
        return param > 0
```

## 🔐 Безопасность разработки

### ✅ DO
- ✅ Используйте параметризованные SQL запросы
- ✅ Валидируйте входные данные
- ✅ Логируйте важные события
- ✅ Используйте try-except для обработки ошибок
- ✅ Шифруйте чувствительные данные

### ❌ DON'T
- ❌ Не используйте string concatenation в SQL
- ❌ Не логируйте пароли и секреты
- ❌ Не создавайте файлы без проверки пути
- ❌ Не используйте eval() или exec()
- ❌ Не сохраняйте пароли в открытом виде

## 📖 Дополнительные ресурсы

### Документация
- [Kivy Docs](https://kivy.org/doc/)
- [Python Docs](https://docs.python.org/3/)
- [SQLite Docs](https://www.sqlite.org/docs.html)

### Полезные инструменты
- `pylint` - статический анализ кода
- `black` - форматирование кода
- `pytest` - расширенное тестирование
- `coverage` - покрытие кода тестами

### Установка инструментов
```bash
pip install pylint black pytest coverage
```

## 🚀 Процесс разработки

### 1. Создать ветку (если используете Git)
```bash
git checkout -b feature/new-feature
```

### 2. Написать код
```bash
# Редактировать файлы
```

### 3. Тестировать
```bash
python tests.py
pylint app/*.py
black app/
```

### 4. Коммитить
```bash
git commit -m "Добавлена новая функция"
```

### 5. Создать Pull Request

## 📱 Тестирование на Android

### 1. Собрать debug APK
```bash
buildozer android debug
```

### 2. Установить на устройство
```bash
adb install -r bin/steamauth-1.0-debug.apk
```

### 3. Просмотреть логи
```bash
adb logcat | grep python
```

### 4. Отладка
```bash
adb shell
am start -D org.steamauth.steamauth/.SteamAuthApp
```

## 🎯 Common Issues & Solutions

### Проблема: Kivy не запускается
**Решение**: 
```bash
pip install --upgrade kivy
pip install kivy[full]
```

### Проблема: SQLite Database is locked
**Решение**: 
```python
conn.commit()  # Не забывайте коммитить транзакции
conn.close()   # Закрывайте соединения
```

### Проблема: Import Error
**Решение**: 
```bash
# Убедитесь что находитесь в правильной папке
cd steam_auth
# Добавьте текущую папку в PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

**Happy Coding! 🚀**
