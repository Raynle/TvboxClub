import os
from flask import Blueprint, make_response, request
from bs4 import BeautifulSoup
import re

# Создаем Blueprint для плагина
news_enhancements_bp = Blueprint('news_enhancements', __name__)

# Функция для обработки текста: поддержка абзацев и переносов строк
def enhanced_format_bbcode(text):
    text = re.sub(r'\n+', '<br>', text)
    if '<br>' in text:
        paragraphs = text.split('<br>')
        text = ''.join(f'<p>{p}</p>' for p in paragraphs if p.strip())
    return text

# Middleware для внедрения изменений
def inject_enhancements(response):
    if 'text/html' not in response.content_type:
        return response

    soup = BeautifulSoup(response.data, 'html.parser')

    # 1. Добавляем чекбоксы в формы и уменьшаем поля
    if '/admin/add_news' in request.url or '/admin/edit/' in request.url:
        form = soup.find('form')
        if form and soup.head:
            category_select = form.find('select', {'name': 'category'})
            android_input = form.find('input', {'name': 'android'})
            version_input = form.find('input', {'name': 'version'})
            modification_input = form.find('input', {'name': 'modification'})

            # Уменьшаем поля и добавляем чекбоксы после них в одном контейнере
            if category_select:
                category_select['style'] = 'width: 200px !important;'
                category_container = soup.new_tag('div', style='display: inline-flex; align-items: center; margin-bottom: 10px;')
                category_select.wrap(category_container)
                category_checkbox = BeautifulSoup('<label style="margin-left: 10px;"><input type="checkbox" name="hide_category"> Показать кат</label>', 'html.parser')
                category_select.parent.append(category_checkbox)

            if android_input:
                android_input['style'] = 'width: 200px !important;'
                android_container = soup.new_tag('div', style='display: inline-flex; align-items: center; margin-bottom: 10px;')
                android_input.wrap(android_container)
                android_checkbox = BeautifulSoup('<label style="margin-left: 10px;"><input type="checkbox" name="hide_android"> Показать Andr</label>', 'html.parser')
                android_input.parent.append(android_checkbox)

            if version_input:
                version_input['style'] = 'width: 200px !important;'
                version_container = soup.new_tag('div', style='display: inline-flex; align-items: center; margin-bottom: 10px;')
                version_input.wrap(version_container)
                version_checkbox = BeautifulSoup('<label style="margin-left: 10px;"><input type="checkbox" name="hide_version"> Показать вер</label>', 'html.parser')
                version_input.parent.append(version_checkbox)

            if modification_input:
                modification_input['style'] = 'width: 200px !important;'
                modification_container = soup.new_tag('div', style='display: inline-flex; align-items: center; margin-bottom: 10px;')
                modification_input.wrap(modification_container)
                modification_checkbox = BeautifulSoup('<label style="margin-left: 10px;"><input type="checkbox" name="hide_modification"> Показать Мод</label>', 'html.parser')
                modification_input.parent.append(modification_checkbox)

            # При редактировании проставляем чекбоксы
            if '/admin/edit/' in request.url:
                news_list = load_news()
                slug = request.url.split('/')[-1]
                news = next((n for n in news_list if n['slug'] == slug), None)
                if news:
                    for field in ['category', 'android', 'version', 'modification']:
                        hide_field = f'hide_{field}'
                        is_hidden = news.get(hide_field, True)  # По умолчанию скрыто
                        checkbox = form.find('input', {'name': hide_field})
                        if checkbox and not is_hidden:  # Отмечаем, если НЕ скрыто
                            checkbox['checked'] = 'checked'

    # 2. Добавляем стили
    if soup.head:
        styles = """
        <style>
            .news-item p, .full-description p, article p {
                word-wrap: break-word;
                white-space: normal;
                overflow-wrap: break-word;
                margin: 0 0 10px 0;
            }
            .news-item p:not(:last-child), .full-description p:not(:last-child), article p:not(:last-child) {
                margin-bottom: 10px;
            }
            /* Скрываем все поля в news-meta по умолчанию */
            .news-meta p {
                display: none;
            }
            /* Показываем, если есть класс visible */
            .news-meta p.visible {
                display: block !important;
            }
            /* Адаптация для смартфонов */
            @media (max-width: 600px) {
                div[style*="display: inline-flex"] {
                    display: block;
                }
                select[name="category"], input[name="android"], input[name="version"], input[name="modification"] {
                    width: 150px !important;
                }
                label {
                    margin-top: 5px;
                }
            }
        </style>
        """
        soup.head.append(BeautifulSoup(styles, 'html.parser'))

    # 3. Скрываем или показываем поля на главной и страницах новостей
    news_list = load_news()
    articles = soup.find_all('article')
    for article in articles:
        news = None
        # Для главной страницы или /news (поиск через news-link)
        news_link = article.find('a', class_='news-link')
        if news_link:
            news_slug = news_link['href'].split('/')[-1].rstrip('/')
            news = next((n for n in news_list if n['slug'] == news_slug), None)
        # Для страницы новости (/<slug>)
        else:
            slug = request.url.strip('/').split('/')[-1]
            news = next((n for n in news_list if n['slug'] == slug), None)

        if news:
            meta = article.find('div', class_='news-meta')
            if meta:
                meta_items = meta.find_all('p')
                for item in meta_items:
                    text = item.get_text(strip=True).lower()
                    if 'категория' in text:
                        item['class'] = item.get('class', []) + ['category']
                    elif 'android' in text:
                        item['class'] = item.get('class', []) + ['android']
                    elif 'версия' in text:
                        item['class'] = item.get('class', []) + ['version']
                    elif 'модификация' in text:
                        item['class'] = item.get('class', []) + ['modification']
                    field = None
                    if 'category' in item['class']:
                        field = 'category'
                    elif 'android' in item['class']:
                        field = 'android'
                    elif 'version' in item['class']:
                        field = 'version'
                    elif 'modification' in item['class']:
                        field = 'modification'
                    if field:
                        is_hidden = news.get(f'hide_{field}', True)  # По умолчанию скрыто
                        if not is_hidden:
                            item['class'] = item.get('class', []) + ['visible']

    response.data = str(soup)
    return response

# Перехватываем только для добавления чекбоксов, без создания/редактирования новостей
def before_request():
    if request.method == 'POST' and ('/admin/add_news' in request.url or '/admin/edit/' in request.url):
        news_list = load_news()
        news_data = {
            'hide_category': 'hide_category' not in request.form,  # Скрыто по умолчанию
            'hide_android': 'hide_android' not in request.form,
            'hide_version': 'hide_version' not in request.form,
            'hide_modification': 'hide_modification' not in request.form,
        }
        if '/admin/add_news' in request.url:
            # Не добавляем новость, оставляем это для app.py
            pass
        else:
            # При редактировании обновляем только поля чекбоксов
            slug = request.url.split('/')[-1]
            for news in news_list:
                if news['slug'] == slug:
                    news.update(news_data)
                    break
            save_news(news_list)

from app import load_news, save_news, app
from datetime import datetime

# Инициализация плагина
def init(flask_app):
    global app
    app = flask_app
    app.register_blueprint(news_enhancements_bp)

    original_format_bbcode = app.jinja_env.filters.get('format_bbcode', lambda x: x)
    def updated_format_bbcode(text):
        text = original_format_bbcode(text)
        text = enhanced_format_bbcode(text)
        return text
    app.jinja_env.filters['format_bbcode'] = updated_format_bbcode

    @app.before_request
    def apply_before_request():
        before_request()

    @app.after_request
    def apply_enhancements(response):
        return inject_enhancements(response)