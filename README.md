# notabug-parser
> *Очень старый проект, который был найден в моих архивах и слегка обновлен под новую версию Scrapy*

Парсер пользователей NotABug, написаный с помощью Scrapy.
Данные сохраняются в json файл.

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

## Запуск
- Устанавливаем зависимости:
```bash
poetry install --no-root
```
- Заходим в корневой раздел проекта:
```bash
cd notabug
```
- Запускаем паука (парсер):
```bash
scrapy crawl notabug -o accounts.json
```
