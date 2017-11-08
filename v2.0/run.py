from flask import Flask
from filters import datetime_filter,marked_filter
app = Flask(__name__)
app.add_template_filter(datetime_filter, 'datetime')
app.add_template_filter(marked_filter, 'marked')
import handlers
import api
import weixin