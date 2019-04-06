from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    pass


from example.views import simple_page

app.register_blueprint(simple_page, url_prefix='/page')
