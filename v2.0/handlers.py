from run import app
from flask import request, render_template,make_response
import time,logging, hashlib
from models import User, Comment, Blog, Message, next_id
from helper import get_page_index, Page
from datetime import datetime

COOKIE_NAME = 'aweSession'
COOKIE_KEY = 'Mblog'


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
                filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


def cookie2user(cookie_str):
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, shal = L
        if int(expires) < time.time():
            return None
        user = User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, COOKIE_KEY)
        if shal != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


@app.before_request
def myredirect():
    request.__user__ = None
    cookie_str = request.cookies.get(COOKIE_NAME)
    if cookie_str:
        user = cookie2user(cookie_str)
        if user:
            logging.info('set current user:%s' % user.email)
            request.__user__ = user


@app.route('/')
def index():
    page = request.args.get('page')
    if page is None:
        page = 1
    date = time.time()
    dt = datetime.fromtimestamp(date)
    page_index = get_page_index(page)
    num = Blog.findNumber('count(id)')
    page = Page(num, page_index)
    if num == 0:
        blogs = []
    else:
        blogs = Blog.findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
    return render_template('blogs.html', page=page, blogs=blogs, dt=dt, __user__=request.__user__)


@app.route('/message')
def message():
    messages = Message.findAll(orderBy='created_at desc')
    return render_template('message.html', messages=messages, __user__=request.__user__)


@app.route('/register')
def register():
    return render_template('register.html', __user__=request.__user__)


@app.route('/signin')
def signin():
    return render_template('signin.html', __user__=request.__user__)


@app.route('/signout')
def signout():
    referer = request.headers.get('Referer')
    r = make_response()
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    return r


@app.route('/blog/<id>')
def get_blog(id):
    blog = Blog.find(id)
    comments = Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    return render_template('blog.html', blog=blog, comments=comments, __user__=request.__user__)


@app.route('/manage/blogs/create')
def manage_create_blog():
    return render_template('manage_blog_edit.html', id='', action='/api/blogs', __user__=request.__user__)


@app.route('/manage/blogs/edit')
def manage_edit_blog():
    id = request.args.get('id')
    return render_template('manage_blog_edit.html', id=id, action='/api/blogs/%s' % id, __user__=request.__user__)


@app.route('/manage/blogs')
def manage_blogs():
    page = request.args.get('page')
    if page is None:
        page = 1
    page_index = get_page_index(page)
    num = Blog.findNumber('count(id)')
    page = Page(num, page_index)
    return render_template('manage_blogs.html', page=page, __user__=request.__user__)


@app.route('/about')
def manage_aboutme():
    return render_template('aboutme.html', __user__=request.__user__)
