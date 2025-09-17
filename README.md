# 🕷️ notabug-parser

> Старый скрипт из архивов — воскрешён и адаптирован под современный Scrapy.  
> Парсит профили пользователей [NotABug.org](https://notabug.org) → сохраняет в `JSON`.

---

## 📦 Установка и запуск

```bash
# Установите зависимости
poetry install --no-root

# Перейдите в папку проекта
cd notabug

# Запустите парсер
scrapy crawl notabug -o accounts.json
```

Результат — в `notabug/accounts.json`.

---

## 🌐 Использование бесплатных прокси (опционально)

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

---

## 📂 Структура (кратко)

```
notabug/
├── scrapy.cfg
├── notabug/              # основной модуль Scrapy
│   ├── spiders/notabug.py
│   └── settings.py
├── accounts.json         # сюда пишутся данные
├── pyproject.toml
└── poetry.lock
```

---

## 💡 Пример вывода

```json
{
    "avatar": "https://notabug.org/avatars/234?s=290",
    "username": "vimuser",
    "repositories": [
        {
            "title": "oachecker",
            "url": "https://notabug.org/vimuser/oachecker",
            "stars": 0,
            "branches": 0,
            "last_updated": "2 лет назад",
            "description": "really half-assed thing i half-assed in 2012"
        },
        // ...
    ],
    "organizations": [
        {
            "icon": "https://notabug.org/avatars/6431",
            "link": "https://notabug.org/libreboot"
        },
        // ...
    ],
    "location": "IRC",
    "link": "https://libreboot.org/",
    "joined": "Присоединился Apr 05, 2015",
    "followers": 40,
    "following": 4
}
```

---

> ⚠️ Для образовательных/архивных целей. Используйте ответственно.

---
