
def init(app):
    import os
    import json
    from flask import request, session, redirect, url_for, render_template_string

    REPORTS_FILE = 'reports.json'
    TEMPLATE_FILE = 'reports_template.html'

    DEFAULT_TEMPLATE = """
    <!DOCTYPE html>
    <html><head><meta charset="utf-8">
    <title>Р–Р°Р»РѕР±С‹</title>
    <style>
        body { background: #111; color: #fff; font-family: sans-serif; padding: 20px; }
        .report { background: #222; padding: 10px; margin: 10px 0; border-radius: 6px; }
        button { background: #f33; color: white; border: none; padding: 5px 10px; cursor: pointer; }
        a { color: #1e90ff; text-decoration: none; }
    </style>
    </head><body>
    <h1>Р–Р°Р»РѕР±С‹ ({{ reports|length }})</h1>
    {% for r in reports %}
        <div class="report">
            <p><b>РўРёРї:</b> {{ r.type }}</p>
            <p><b>Р¦РµР»СЊ:</b> <a href="/{{ r.target }}">{{ r.target }}</a></p>
            <p><b>РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ:</b> {{ r.user }} | IP: {{ r.ip }}</p>
            <p><b>РџСЂРёС‡РёРЅР°:</b> {{ r.reason }}</p>
            <form method="post" action="/admin/reports/delete/{{ loop.index0 }}">
                <button type="submit">РЈРґР°Р»РёС‚СЊ Р¶Р°Р»РѕР±Сѓ</button>
            </form>
        </div>
    {% else %}
        <p>Р–Р°Р»РѕР± РЅРµС‚.</p>
    {% endfor %}
    </body></html>
    """

    def load_reports():
        if os.path.exists(REPORTS_FILE):
            with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_reports(reports):
        with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)

    def load_template():
        if os.path.exists(TEMPLATE_FILE):
            with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        return DEFAULT_TEMPLATE

    def save_template(content):
        with open(TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            f.write(content)

    @app.route('/report/<type>/<target>', methods=['GET', 'POST'])
    def report_submit(type, target):
        if 'user' not in session and 'admin' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            reason = request.form.get('reason')
            if reason:
                reports = load_reports()
                reports.append({
                    'type': type,
                    'target': target,
                    'reason': reason,
                    'user': session.get('user', 'anon'),
                    'ip': request.remote_addr
                })
                save_reports(reports)
                return '<p>Р–Р°Р»РѕР±Р° РѕС‚РїСЂР°РІР»РµРЅР°. <a href="/">Р’РµСЂРЅСѓС‚СЊСЃСЏ</a></p>'
        return f'''
        <html><body style="background:#111;color:#fff;font-family:sans-serif;padding:20px">
        <h2>РџРѕР¶Р°Р»РѕРІР°С‚СЊСЃСЏ РЅР° {type}</h2>
        <form method="post">
            <input name="reason" placeholder="РџСЂРёС‡РёРЅР° Р¶Р°Р»РѕР±С‹" style="width:300px" required>
            <button type="submit">РћС‚РїСЂР°РІРёС‚СЊ</button>
        </form>
        </body></html>
        '''

    @app.route('/admin/reports')
    def view_reports():
        if 'admin' not in session:
            return redirect(url_for('admin'))
        return render_template_string(load_template(), reports=load_reports())

    @app.route('/admin/reports/delete/<int:index>', methods=['POST'])
    def delete_report(index):
        if 'admin' not in session:
            return redirect(url_for('admin'))
        reports = load_reports()
        if 0 <= index < len(reports):
            reports.pop(index)
            save_reports(reports)
        return redirect(url_for('view_reports'))

    @app.after_request
    def inject_complaint_buttons(response):
        if response.content_type.startswith('text/html'):
            try:
                html = response.get_data(as_text=True)

                if 'class="news-content"' in html:
                    html = html.replace(
                        '</div>', 
                        '<form method="get" action="/report/news/current">'
                        '<button style="margin-top:10px;background:#f33;color:white;">РџРѕР¶Р°Р»РѕРІР°С‚СЊСЃСЏ РЅР° РЅРѕРІРѕСЃС‚СЊ</button>'
                        '</form></div>', 1)

                if 'class="comment-item"' in html:
                    html = html.replace(
                        '</div>', 
                        '<form method="get" action="/report/comment/current">'
                        '<button style="margin-top:5px;margin-left:10px;background:#f33;color:white;">РџРѕР¶Р°Р»РѕРІР°С‚СЊСЃСЏ</button>'
                        '</form></div>', 1)

                response.set_data(html)
            except Exception:
                pass
        return response