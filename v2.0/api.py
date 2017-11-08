from run import app
from flask import request, make_response
from handlers import COOKIE_KEY, COOKIE_NAME, user2cookie
import re, time, json, logging, hashlib, base64
from models import User, Comment, Blog, Message, next_id
from helper import Page, get_page_index

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        return False
    else:
        return True


@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    email = data.get('email')
    passwd = data.get('passwd')
    if not email:
        e = {'error': 'value:invalid', 'data': 'email', 'message': 'Invalid email'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    if not passwd:
        e = {'error': 'value:invalid', 'data': 'passwd', 'message': 'Invalid password'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    users = User.findAll('email=?', [email])
    if len(users) == 0:
        e = {'error': 'value:invalid', 'data': 'email', 'message': 'Email not exist'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    user = users[0]
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        e = {'error': 'value:invalid', 'data': 'passwd', 'message': 'Invalid password'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    user2 = user.copy()
    user2['passwd'] = '******'
    r = make_response(json.dumps(user2, ensure_ascii=False).encode('utf-8'))
    r.headers['Content-Type'] = 'application/json'
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    return r


@app.route('/api/users', methods=['POST'])
def api_register_user():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    passwd = data.get('passwd')
    if not name or not name.strip():
        e = {'error': 'value:invalid', 'data': 'name', 'message': ''}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    if not email or not _RE_EMAIL.match(email):
        e = {'error': 'value:invalid', 'data': 'email', 'message': ''}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    if not passwd or not _RE_SHA1.match(passwd):
        e = {'error': 'value:invalid', 'data': 'passwd', 'message': ''}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    users = User.findAll('email=?', [email])
    if len(users) > 0:
        e = {'error': 'value:invalid', 'data': 'email', 'message': 'Email is already in use'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    user.save()
    r = make_response(json.dumps(user, ensure_ascii=False).encode('utf-8'))
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    r.content_type = 'application/json'
    return r


@app.route('/api/blogs/<id>', methods=['GET'])
def api_get_blog(id):
    blog = Blog.find(id)
    return json.dumps(blog)


@app.route('/api/blogs', methods=['GET'])
def api_blogs():
    page = request.args.get('page')
    if page is None:
        page = '1'
    page_index = get_page_index(page)
    num = Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return json.dumps(dict(page=p, blogs=()))
    blogs = Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return json.dumps(dict(page=p.__dict__, blogs=blogs))


@app.route('/api/blogs', methods=['POST'])
def api_create_blog():
    if not check_admin(request):
        e = {'error': 'permission:forbidden', 'data': 'permission', 'message': ''}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    data = request.get_json()
    name = data.get('name')
    summary = data.get('summary')
    content = data.get('content')
    if not name or not name.strip():
        e = {'error': 'value:invalid', 'data': 'name', 'message': 'name cannot be empty'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    if not summary or not summary.strip():
        e = {'error': 'value:invalid', 'data': 'summary', 'message': 'summary cannot be empty'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    if not content or not content.strip():
        e = {'error': 'value:invalid', 'data': 'content', 'message': 'content cannot be empty'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image,
                name=name.strip(), summary=summary.strip(), content=content.strip())
    blog.save()
    return json.dumps(blog.__dict__)


@app.route('/api/blogs/<id>', methods=['POST'])
def api_update_blog(id):
    if not check_admin(request):
        e = {'error': 'permission:forbidden', 'data': 'permission', 'message': ''}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    data = request.get_json()
    name = data.get('name')
    summary = data.get('summary')
    content = data.get('content')
    blog = Blog.find(id)
    if not name or not name.strip():
        e = {'error': 'value:invalid', 'data': 'name', 'message': 'name cannot be empty'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    if not summary or not summary.strip():
        e = {'error': 'value:invalid', 'data': 'summary', 'message': 'summary cannot be empty'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    if not content or not content.strip():
        e = {'error': 'value:invalid', 'data': 'content', 'message': 'content cannot be empty'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    blog.update()
    return json.dumps(blog.__dict__)


@app.route('/api/blogs/<id>/delete', methods=['POST'])
def api_delete_blog(id):
    if not check_admin(request):
        e = {'error': 'permission:forbidden', 'data': 'permission', 'message': ''}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    blog = Blog.find(id)
    blog.remove()
    return json.dumps(dict(id=id))


@app.route('/api/blogs/<id>/comments', methods=['POST'])
def api_create_comment(id):
    user = request.__user__
    content = request.get_json().get('content')
    if user is None:
        e = {'error': 'permission:forbidden', 'data': 'Please signin first.', 'message': ''}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    if not content or not content.strip():
        e = {'error': 'value:invalid', 'data': 'content', 'message': 'content cannot be empty'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    blog = Blog.find(id)
    if blog is None:
        e = {'error': 'value:not found', 'data': 'blog', 'message': ''}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image,
                      content=content.strip())
    comment.save()
    return json.dumps(comment.__dict__)


@app.route('/api/messages', methods=['POST'])
def api_create_message():
    user = request.__user__
    content = request.get_json().get('content')
    if user is None:
        e = {'error': 'permission:forbidden', 'data': 'Please signin first.', 'message': ''}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    if not content or not content.strip():
        e = {'error': 'value:invalid', 'data': 'content', 'message': 'content cannot be empty'}
        r = make_response(json.dumps(e, ensure_ascii=False).encode('utf-8'))
        r.headers['Content-Type'] = 'application/json'
        return r
    message = Message(user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
    message.save()
    return json.dumps(message.__dict__)
