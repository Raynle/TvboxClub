def init(app):
    # HTML-кнопка с квадратной SVG-стрелкой (4-й вариант)
    @app.route('/scroll_to_top_button')
    def scroll_to_top_button():
        return """
        <button id="scroll-to-top" class="scroll-to-top" title="Наверх">
            <svg class="scroll-to-top-icon" xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none">
                <rect width="24" height="24" rx="4" fill="#F1F1F1" stroke="#000" stroke-width="2"/>
                <path d="M12 8L8 12H11V16H13V12H16L12 8Z" fill="#333"/>
            </svg>
        </button>
        """

    # CSS
    @app.route('/static/scroll_to_top.css')
    def scroll_to_top_css():
        return """
        .scroll-to-top {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: none;
            border: none;
            width: 40px;
            height: 40px;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.3s, transform 0.3s;
            z-index: 1000;
            padding: 0;
        }
        .scroll-to-top.visible {
            opacity: 1;
            transform: translateY(0);
        }
        .scroll-to-top:hover {
            transform: translateY(-5px);
        }
        .scroll-to-top-icon {
            width: 100%;
            height: 100%;
        }
        """, 200, {'Content-Type': 'text/css'}

    # JS
    @app.route('/static/scroll_to_top.js')
    def scroll_to_top_js():
        return """
        document.addEventListener('DOMContentLoaded', () => {
            const scrollButton = document.createElement('button');
            scrollButton.id = 'scroll-to-top';
            scrollButton.className = 'scroll-to-top';
            scrollButton.title = 'Наверх';
            scrollButton.innerHTML = `
                <svg class="scroll-to-top-icon" xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none">
                    <rect width="24" height="24" rx="4" fill="#F1F1F1" stroke="#000" stroke-width="2"/>
                    <path d="M12 8L8 12H11V16H13V12H16L12 8Z" fill="#333"/>
                </svg>
            `;
            document.body.appendChild(scrollButton);

            const button = document.getElementById('scroll-to-top');
            if (button) {
                window.addEventListener('scroll', () => {
                    if (window.scrollY > 300) {
                        button.classList.add('visible');
                    } else {
                        button.classList.remove('visible');
                    }
                });
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                });
            }
        });
        """, 200, {'Content-Type': 'text/javascript'}

    def add_scroll_to_top():
        return scroll_to_top_button()
    
    app.jinja_env.globals['add_scroll_to_top'] = add_scroll_to_top

    @app.after_request
    def inject_scroll_to_top_resources(response):
        if response.content_type.startswith('text/html'):
            html = response.get_data(as_text=True)
            if '</head>' in html:
                css = '<link rel="stylesheet" href="/static/scroll_to_top.css">'
                html = html.replace('</head>', f'{css}</head>')
            if '</body>' in html:
                js = '<script src="/static/scroll_to_top.js"></script>'
                html = html.replace('</body>', f'{js}</body>')
            response.set_data(html)
        return response