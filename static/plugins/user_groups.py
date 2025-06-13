import os
import json
from flask import session, redirect, url_for, request, render_template

def init(app):
    @app.route('/admin/manage_admins_plugin', methods=['GET', 'POST'])  # Изменил маршрут на уникальный
    def manage_admins_plugin():  # Изменил имя функции
        if 'admin' not in session:
            return redirect(url_for('admin'))
        
        admins = load_admins()
        users = load_users()
        search_query = request.form.get('search_query', '').lower() if request.method == 'POST' and 'search_query' in request.form else ''
        
        filtered_users = [user for user in users if search_query in user['login'].lower()] if search_query else users
        
        if request.method == 'POST' and 'action' in request.form:
            action = request.form.get('action')
            username = request.form.get('username')
            
            if action == 'add' and username:
                if username not in admins and username in [user['login'] for user in users]:
                    admins.append(username)
                    save_admins(admins)
                    # Если это текущий пользователь, обновляем права сразу
                    if username == session.get('user'):
                        session['admin'] = True
            elif action == 'remove' and username in admins:
                admins.remove(username)
                save_admins(admins)
                if username == session.get('user'):
                    session.pop('admin', None)
                    session.pop('user', None)
                    return redirect(url_for('login'))
            
            return redirect(url_for('manage_admins_plugin'))  # Обновил редирект
        
        theme = session.get('theme', 'dark')
        categories = load_categories()
        icons = load_icons()
        return render_template('admin.html', categories=categories, theme=theme, settings=load_settings(), icons=icons, show_manage_admins=True, admins=admins, users=filtered_users, search_query=search_query)

def load_admins():
    if os.path.exists('admins.json'):
        with open('admins.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_admins(admins):
    with open('admins.json', 'w', encoding='utf-8') as f:
        json.dump(admins, f, ensure_ascii=False, indent=2)

def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def load_categories():
    if os.path.exists('categories.json'):
        with open('categories.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def load_settings():
    if os.path.exists('settings.json'):
        with open('settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"registration_enabled": True}

def load_icons():
    default_icons = {
        "category": {"emoji": "📁", "custom": None},
        "android": {"emoji": "🤖", "custom": None},
        "version": {"emoji": "🆔", "custom": None},
        "modification": {"emoji": "🔑", "custom": None},
        "settings": {"emoji": "⚙️", "custom": None},
        "closed": {"emoji": "🔒", "custom": None},
        "hidden": {"emoji": "🕶️", "custom": None},
        "views": {"emoji": "👁️", "custom": None},
        "light_theme": {"emoji": "☀️", "custom": None},
        "dark_theme": {"emoji": "🌙", "custom": None},
        "date": {"emoji": "🗓️", "custom": None}
    }
    if os.path.exists('icons.json'):
        try:
            with open('icons.json', 'r', encoding='utf-8') as f:
                loaded_icons = json.load(f)
                for key, value in default_icons.items():
                    if key not in loaded_icons:
                        loaded_icons[key] = value
                return loaded_icons
        except (json.JSONDecodeError, IOError):
            return default_icons
    return default_icons