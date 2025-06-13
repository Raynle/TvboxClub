from flask import request

def init(app):
    # CSS для выравнивания
    @app.route('/static/realign_elements.css')
    def realign_elements_css():
        return """
        .news-item .meta-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 10px;
            width: 100%;
        }
        .news-item .likes {
            display: flex;
            gap: 10px;
            flex-shrink: 0;
        }
        .news-item .views-container {
            flex-grow: 1;
            text-align: center;
        }
        .news-item .news-actions {
            flex-shrink: 0;
        }
        .news-item .admin-actions {
            margin-top: 5px;
            text-align: left;
        }
        /* Для телефонов */
        @media (max-width: 600px) {
            .news-item .meta-container {
                flex-direction: row;
                justify-content: space-between;
            }
            .news-item .views-container {
                flex-grow: 1;
                text-align: center;
            }
            .news-item .news-actions {
                flex-shrink: 0;
            }
        }
        """, 200, {'Content-Type': 'text/css'}

    # JavaScript для обёртки элементов
    @app.route('/static/realign_elements.js')
    def realign_elements_js():
        return """
        document.addEventListener('DOMContentLoaded', () => {
            console.log('Плагин realign_elements.js загружен');
            const newsItems = document.querySelectorAll('.news-item');
            console.log(`Найдено элементов .news-item: ${newsItems.length}`);
            newsItems.forEach(item => {
                const likes = item.querySelector('.likes');
                const views = item.querySelector('.views-container');
                const newsActions = item.querySelector('.news-actions');

                if (likes && views) {
                    const metaContainer = document.createElement('div');
                    metaContainer.className = 'meta-container';
                    likes.parentNode.insertBefore(metaContainer, likes);
                    metaContainer.appendChild(likes);
                    metaContainer.appendChild(views);
                    if (newsActions) metaContainer.appendChild(newsActions);

                    console.log('Элементы выровнены в новости:', item.querySelector('h3')?.textContent);
                } else {
                    console.error('Не все элементы найдены в новости:', {
                        title: item.querySelector('h3')?.textContent,
                        likes: !!likes,
                        views: !!views,
                        newsActions: !!newsActions
                    });
                }
            });
        });
        """, 200, {'Content-Type': 'text/javascript'}

    # Инъекция CSS и JS
    @app.after_request
    def inject_realign_elements(response):
        if response.content_type.startswith('text/html'):
            html = response.get_data(as_text=True)
            if request.path in ['/', '/news'] or request.path.startswith('/youtube-') or request.path.startswith('/admin/'):
                if '</head>' in html:
                    css = '<link rel="stylesheet" href="/static/realign_elements.css">'
                    html = html.replace('</head>', f'{css}</head>')
                if '</body>' in html:
                    js = '<script src="/static/realign_elements.js"></script>'
                    html = html.replace('</body>', f'{js}</body>')
            response.set_data(html)
        return response