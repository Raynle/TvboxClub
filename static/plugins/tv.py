def init(app):
    from flask import render_template_string, request

    messages = []

    @app.route('/tv', methods=['GET', 'POST'])
    def tv_page():
        if request.method == 'POST':
            text = request.form.get('text')
            if text:
                messages.append(text)
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>TV Модуль</title>
            <style>
                body { font-family: sans-serif; background: #111; color: #fff; padding: 20px; }
                input, button { padding: 10px; margin-top: 10px; }
                .message { background: #222; padding: 10px; margin: 5px 0; border-radius: 6px; }
            </style>
        </head>
        <body>
            <h1>📺 Страница TV-модуля</h1>
            <form method="post">
                <input name="text" placeholder="Введите сообщение" required>
                <button type="submit">Отправить</button>
            </form>
            <hr>
            <h2>Сообщения:</h2>
            {% for msg in messages %}
                <div class="message">{{ msg }}</div>
            {% else %}
                <p>Пока ничего нет.</p>
            {% endfor %}
        </body>
        </html>
        ''', messages=messages)