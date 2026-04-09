# ✍️ AI Копирайтер

Генерация продающих текстов для Instagram, Kaspi и сайта по фото товара — за 10 секунд.

## Стек

- Python 3.10+
- Streamlit — веб-интерфейс
- OpenAI GPT-4o Vision — анализ изображения + генерация текста
- Pillow — ресайз изображения перед отправкой в API

## Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd product-copywriter

# 2. Создать виртуальное окружение
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Добавить API-ключ
mkdir .streamlit
echo 'OPENAI_API_KEY = "sk-..."' > .streamlit/secrets.toml

# 5. Запустить
streamlit run app.py
```

Приложение откроется на http://localhost:8501

## Использование

1. Загрузи фото товара (JPG / PNG / WEBP)
2. Введи ключевые слова или краткое описание
3. Нажми **⚡ Сгенерировать тексты**
4. Получи готовые тексты для трёх каналов + скачай JSON

## Структура проекта

```
/
├── app.py              # Весь код приложения
├── requirements.txt    # Зависимости
├── README.md           # Эта инструкция
├── summary.md          # IT4IT-отчёт и рефлексия
└── logs/               # Скриншоты промптов и сессий
```

## Безопасность

- API-ключ хранится в `.streamlit/secrets.toml` — файл добавлен в `.gitignore`
- Ключ никогда не попадает в репозиторий
