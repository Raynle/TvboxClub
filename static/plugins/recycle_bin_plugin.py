import os
import json
from flask import Blueprint, request, session, jsonify, render_template, redirect, url_for
from datetime import datetime

# Создание Blueprint для плагина
recycle_bin_bp = Blueprint('recycle_bin', __name__)

# Путь к файлам (совпадают с app.py)
RECYCLE_BIN_FILE = os.path.join('static', 'plugins', 'recycle_bin.json')
NEWS_FILE = 'news.json'
COMMENTS_FILE = 'comments.json'
os.makedirs(os.path.dirname(RECYCLE_BIN_FILE), exist_ok=True)

# Загрузка и сохранение данных
def load_json(file_path, default=[]):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Загрузка и сохранение корзины
def load_recycle_bin():
    return load_json(RECYCLE_BIN_FILE)

def save_recycle_bin(data):
    save_json(RECYCLE_BIN_FILE, data)

# Перехват удаления новостей
@recycle_bin_bp.before_app_request
def intercept_news_deletion():
    if request.path.startswith('/admin/delete/') and request.method == 'GET' and 'admin' in session:
        slug = request.path.split('/admin/delete/')[1]
        news_list = load_json(NEWS_FILE)
        news = next((n for n in news_list if n.get('slug') == slug), None)
        if news:
            recycle_bin = load_recycle_bin()
            recycle_bin.append({
                'type': 'news',
                'data': news,
                'deleted_by': session.get('user', 'admin'),
                'date_deleted': datetime.now().strftime('%d.%m.%Y %H:%M'),
                'origin': 'admin'
            })
            save_recycle_bin(recycle_bin)
            news_list = [n for n in news_list if n.get('slug') != slug]
            save_json(NEWS_FILE, news_list)

# Перехват удаления комментариев (админ)
@recycle_bin_bp.before_app_request
def intercept_admin_comment_deletion():
    if request.path.startswith('/admin/delete_comment/') and request.method == 'GET' and 'admin' in session:
        comment_id = int(request.path.split('/admin/delete_comment/')[1])
        comments = load_json(COMMENTS_FILE)
        comment = next((c for c in comments if c.get('id') == comment_id), None)
        if comment:
            news_list = load_json(NEWS_FILE)
            news = next((n for n in news_list if n.get('slug') == comment.get('slug')), None)
            recycle_bin = load_recycle_bin()
            recycle_bin.append({
                'type': 'comment',
                'data': comment,
                'deleted_by': session.get('user', 'admin'),
                'date_deleted': datetime.now().strftime('%d.%m.%Y %H:%M'),
                'origin': f'news/{comment.get("slug")} ({news.get("title") if news else "Не найдено"})'
            })
            save_recycle_bin(recycle_bin)
            comments = [c for c in comments if c.get('id') != comment_id]
            save_json(COMMENTS_FILE, comments)

# Перехват удаления комментариев (пользователь)
@recycle_bin_bp.before_app_request
def intercept_user_comment_deletion():
    if request.path.startswith('/delete_comment/') and request.method == 'GET' and 'user' in session:
        comment_id = int(request.path.split('/delete_comment/')[1])
        comments = load_json(COMMENTS_FILE)
        comment = next((c for c in comments if c.get('id') == comment_id), None)
        if comment and (session.get('user') == comment.get('user') or 'admin' in session):
            news_list = load_json(NEWS_FILE)
            news = next((n for n in news_list if n.get('slug') == comment.get('slug')), None)
            recycle_bin = load_recycle_bin()
            recycle_bin.append({
                'type': 'comment',
                'data': comment,
                'deleted_by': session.get('user'),
                'date_deleted': datetime.now().strftime('%d.%m.%Y %H:%M'),
                'origin': f'news/{comment.get("slug")} ({news.get("title") if news else "Не найдено"})'
            })
            save_recycle_bin(recycle_bin)
            comments = [c for c in comments if c.get('id') != comment_id]
            save_json(COMMENTS_FILE, comments)

# Маршрут для страницы корзины
@recycle_bin_bp.route('/recycle_bin')
def recycle_bin_page():
    if 'admin' not in session:
        return redirect(url_for('login'))
    recycle_bin = load_recycle_bin()
    return render_template('recycle_bin.html', recycle_bin=recycle_bin, theme=session.get('theme', 'dark'), icons=load_json('icons.json', {}), session=session)

# Обработка восстановления или удаления
@recycle_bin_bp.route('/recycle_bin/action', methods=['POST'])
def recycle_bin_action():
    if 'admin' not in session:
        return redirect(url_for('login'))
    recycle_bin = load_recycle_bin()
    action = request.form.get('action')
    item_id = int(request.form.get('id'))
    item = next((i for i in recycle_bin if recycle_bin.index(i) == item_id), None)
    
    if item and action == 'restore':
        if item['type'] == 'news':
            news_list = load_json(NEWS_FILE)
            news_list.insert(0, item['data'])
            save_json(NEWS_FILE, news_list)
        elif item['type'] == 'comment':
            comments = load_json(COMMENTS_FILE)
            comments.append(item['data'])
            save_json(COMMENTS_FILE, comments)
        recycle_bin.pop(item_id)
        save_recycle_bin(recycle_bin)
    elif item and action == 'delete':
        recycle_bin.pop(item_id)
        save_recycle_bin(recycle_bin)
    
    return redirect(url_for('recycle_bin.recycle_bin_page'))

def init(app):
    app.register_blueprint(recycle_bin_bp, url_prefix='/')