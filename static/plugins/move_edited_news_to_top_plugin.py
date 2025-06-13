import os
import json
from flask import Blueprint, request, session

move_edited_news_to_top_bp = Blueprint('move_edited_news_to_top', __name__)

NEWS_FILE = 'news.json'

def load_json(file_path, default=[]):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@move_edited_news_to_top_bp.before_app_request
def move_edited_news_to_top():
    if request.path.startswith('/admin/edit/') and request.method == 'POST' and 'admin' in session:
        slug = request.path.split('/admin/edit/')[1]
        news_list = load_json(NEWS_FILE)
        # Находим новость по slug
        edited_news = next((news for news in news_list if news.get('slug') == slug), None)
        if edited_news:
            # Удаляем новость из текущего места
            news_list = [news for news in news_list if news.get('slug') != slug]
            # Добавляем её в начало списка
            news_list.insert(0, edited_news)
            # Сохраняем обновлённый список
            save_json(NEWS_FILE, news_list)

def init(app):
    app.register_blueprint(move_edited_news_to_top_bp, url_prefix='/')