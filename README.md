# 🕷️ notabug-parser

> Старый скрипт из архивов — воскрешён и адаптирован под современный Scrapy.  

> В некоторых местах намеренно применяются разные подходы к решению одной и той же задачи (например, использование как `xpath`, так и `css`, ручной парсинг и `ItemLoader`, прямые вызовы и `callback`-передача данных). Это сделано сознательно — чтобы попрактиковаться в различных техниках, предоставляемых Scrapy.

> Парсит профили пользователей организации и репозитории [NotABug.org](https://notabug.org) → сохраняет в `JSON Lines` формате.

---

## 📦 Установка и запуск

### Poetry

```bash
# Установите зависимости
poetry install --no-root

# Перейдите в папку проекта
cd notabug

# Запустите парсер
poetry run scrapy crawl notabug
```

### pip

```bash
# Создайте виртуальное окружение
python -m venv .venv

# Активируйте его
source .venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Перейдите в папку проекта
cd notaubg

# Запустите парсер
scrapy crawl notabug
```

Результат сохраняется в трёх файлах в формате **JSONL** (JSON Lines):

- `accounts.jsonl` — профили пользователей  
- `organizations.jsonl` — организации  
- `repos.jsonl` — репозитории

> 💡 Формат JSONL позволяет легко обрабатывать большие объёмы данных построчно (например, через `jq`, Pandas или Spark).

---

## 🗃️ Структура данных

### `AccountItem`
```json
{
  "url": "https://notabug.org/vimuser",
  "username": "vimuser",
  "avatar": "https://seccdn.libravatar.org/avatar/...",
  "joined": "2017-03-24 00:00:00",
  "link": "https://libreboot.org/",
  "location": "IRC",
  "followers": 40,
  "following": 4
}
```

### `OrganizationItem`
```json
{
  "url": "https://notabug.org/libreboot",
  "name": "libreboot",
  "joined": "2017-03-24 00:00:00",
  "icon": "https://seccdn.libravatar.org/avatar/...",
  "description": "Free (as in freedom) boot firmware...",
  "link": "https://libreboot.org",
  "location": null,
  "persons": ["/vimuser", "/leah"]
}
```

### `RepositoryItem`
```json
{
  "url": "https://notabug.org/jadedctrl/wrdk",
  "owner": "jadedctrl",
  "title": "wrdk",
  "last_updated": "2020-05-31 07:09:50",
  "stars": 0,
  "branches": 0,
  "description": "Mirror of the WikiReader Development Kits repository",
  "commits": 1,
  "releases": 0,
  "issues": 0,
  "pulls": 0,
  "forks": 0,
  "watchers": 0
}
```

> ⚠️ Все даты автоматически **парсятся в `datetime`** и сериализуются.  

> Числовые поля (`stars`, `followers` и т.д.) — **целые числа**, даже если изначально были строками.

---

## ⚙️ Настройки

Проект использует **три отдельных фида** в `settings.py`:

```python
from .items import AccountItem, RepositoryItem, OrganizationItem

FEEDS = {
    "accounts.jsonl": {
        "format": "jsonl", 
        "overwrite": False, 
        "item_classes": [AccountItem]
    },
    "repos.jsonl": {
        "format": "jsonl", 
        "item_classes": [RepositoryItem]
    },
    "organizations.jsonl": {
        "format": "jsonl", 
        "item_classes": [OrganizationItem]
    }
}
```

Можно расскомментировать строку с JOBDIR, для возобновления парсера после его отключения:
```python
JOBDIR = 'crawl-job/'
```

И включить запись логов в файл:
```python
LOG_FILE = "crawl.log"
```

Также включены пайплайны для:
- очистки строк (`StripStringsPipeline`)
- нормализации дат (`JoinedCleanPipeline`)
- конвертации типов (`ConvertToCorrectTypesPipeline`)

---

### 🌐 Использование бесплатных прокси (опционально)

Если вы хотите использовать бесплатные прокси для анонимности или обхода блокировок, раскомментируйте следующие строки в `notabug/notabug/settings.py`:

```python
PROXY_POOL_ENABLED = True
```

и в разделе `DOWNLOADER_MIDDLEWARES`:

```python
DOWNLOADER_MIDDLEWARES = {
    # ...
    'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
    'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
    # ...
}
```

> 💡 Это подключит [scrapy-proxy-pool](https://github.com/rejoiceinhope/scrapy-proxy-pool ) — middleware, которое автоматически ротирует бесплатные прокси из публичных списков.  

> Полезно при частом парсинге, чтобы избежать блокировки по IP.

> 🔒 NotABug.org не агрессивно блокирует ботов, но при массовом парсинге прокси могут помочь.

---

## 📂 Структура проекта

```
notabug/
├── scrapy.cfg
├── pyproject.toml
├── notabug/
│   ├── __init__.py
│   ├── items.py          # dataclass-модели
│   ├── pipelines.py      # обработка и конвертация
│   ├── settings.py
│   └── spiders/
│       └── notabug.py    # основной спайдер
├── accounts.jsonl        # ← результат
├── organizations.jsonl   # ← результат
└── repos.jsonl           # ← результат
```

---

> ⚠️ Для образовательных/архивных целей. Используйте ответственно.

---
