# при рендеринге страниц используются правильные шаблоны

def test_root_template(client, captured_templates):
    with captured_templates as templates:
        client.get('/')
    assert len(templates) == 1
    template, context = templates[0]
    assert template.name == 'index.html'

def test_posts_template(client, captured_templates, mocker, posts_list):
    mocker.patch(
        'app.posts_list',
        return_value = posts_list,
        autospec = True
    )
    with captured_templates as templates:        
        client.get('/posts')
    assert len(templates) == 1
    template, context = templates[0]
    assert template.name == 'posts.html'

def test_post_template(client, captured_templates, mocker, posts_list):
    mocker.patch(
        'app.posts_list',
        return_value = posts_list,
        autospec = True
    )
    with captured_templates as templates:
        client.get('/posts/0')
    assert len(templates) == 1
    template, context = templates[0]
    assert template.name == 'post.html'

def test_about_template(client, captured_templates):
    with captured_templates as templates:
        client.get('/about')
    assert len(templates) == 1
    template, context = templates[0]
    assert template.name == 'about.html'



# в шаблоны передаются все необходимые данные

def test_root_context(client, captured_templates):
    with captured_templates as templates:
        client.get('/')
    template, context = templates[0]
    assert len(context) == 3

def test_posts_context(client, captured_templates, mocker, posts_list):
    mocker.patch(
        'app.posts_list',
        return_value = posts_list,
        autospec = True
    )
    with captured_templates as templates:
        client.get('/posts')
    template, context = templates[0]
    assert context['title'] == 'Посты'
    assert len(context['posts']) == len(posts_list)

def test_post_context(client, captured_templates, mocker, posts_list):
    mocker.patch(
        'app.posts_list',
        return_value = posts_list,
        autospec = True
    )
    with captured_templates as templates:
        client.get('/posts/0')
    template, context = templates[0]
    assert context['title'] == posts_list[0]['title']
    assert context['post'] == posts_list[0]

def test_about_context(client, captured_templates):
    with captured_templates as templates:
        client.get('/about')
    template, context = templates[0]
    assert context['title'] == 'Об авторе'



# в результате рендеринга на странице присутствуют все данные поста (заголовок, текст, имя автора и т. д.)

def test_post_title(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get('/posts/0')
    assert posts_list[0]['title'] in response.text

def test_post_text(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get('/posts/0')
    assert posts_list[0]['text'] in response.text

def test_post_author(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get('/posts/0')
    assert posts_list[0]['author'] in response.text

# дата публикации отображается в правильном формате

def test_post_date(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get('/posts/0')
    assert posts_list[0]['date'].strftime('%d.%m.%Y') in response.text

def test_post_image_id(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get('/posts/0')
    assert posts_list[0]['image_id'] in response.text

def test_post_comments_authors(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get('/posts/0')
    for comment_i in range (len(posts_list[0]['comments'])):
        assert posts_list[0]['comments'][comment_i]['author'] in response.text

def test_post_comments_texts(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get('/posts/0')
    for comment_i in range (len(posts_list[0]['comments'])):
        assert posts_list[0]['comments'][comment_i]['text'] in response.text

def test_post_comments_replies_authors(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get('/posts/0')
    for comment_i in range (len(posts_list[0]['comments'])):
        for reply_i in range (len(posts_list[0]['comments'][comment_i]['replies'])):
            assert posts_list[0]['comments'][comment_i]['replies'][reply_i]['author'] in response.text

def test_post_comments_replies_texts(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    response = client.get('/posts/0')
    for comment_i in range (len(posts_list[0]['comments'])):
        for reply_i in range (len(posts_list[0]['comments'][comment_i]['replies'])):
            assert posts_list[0]['comments'][comment_i]['replies'][reply_i]['text'] in response.text



# при попытке получить доступ по несуществующему идентификатору поста приложение вернёт код состояния 404.

def test_post_index_nonexisting(client, mocker, posts_list):
    mocker.patch(
        "app.posts_list",
        return_value=posts_list,
        autospec=True
    )
    for post_i in [-1, 1, 'n']:
        response = client.get(f"/posts/{post_i}")
        assert response.status_code == 404
