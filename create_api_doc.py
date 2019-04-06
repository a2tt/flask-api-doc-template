import importlib
import re
import argparse
import sys
import os
import random
import string
from collections import defaultdict, OrderedDict
from urllib.parse import unquote

import rstr
from flask import url_for

from templates import *


def rand_key_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def verbose_message(message):
    if verbosity:
        print(message)


def refine_methods(methods: set, target=None):
    if target is None:
        target = {'OPTIONS', 'HEAD'}
    return methods - set(target)


def fix_url_converter(converters):
    for name, cls in converters.items():
        if name in ['default', 'string', 'any']:
            cls.regex = '[0-9a-zA-Z]+'


def list_routes(app):
    param_p = re.compile('<[a-zA-Z0-9:_]*>')
    converters = app.url_map.converters
    fix_url_converter(converters)  # any string regex to refined

    apis = []

    with app.app_context():
        for rule in app.url_map.iter_rules():
            # parse url arguments. ex) '/foo/<int:id>/<something:value>' to ['int:id', 'something:value']
            url_args = list(map(lambda d: d[1:-1], param_p.findall(str(rule))))
            arguments = {}

            for idx, arg in enumerate(url_args):
                type_ = 'default'
                arg_name = arg
                if arg.find(':') != -1:
                    type_, arg_name = tuple(arg.split(':'))

                # To prevent unnecessary characters, generate some types manually
                if type_ in ['int', 'float']:
                    # As url.replace below can mistakenly replace other arguments, make 10 digits value (of course it's bad idea)
                    # url_for accept '001' as 1 if arg type is int. so cast in to str
                    arguments[arg_name] = str(int(rand_key_generator(10, string.digits)))
                elif type_ in ['default', 'string', 'any']:
                    arguments[arg_name] = rand_key_generator(10)
                else:
                    try:
                        convt = converters.get(type_, 'default')
                        arg_value = rstr.xeger(convt.regex)  # random string that matches regex
                        arguments[arg_name] = arg_value
                    except AttributeError:
                        raise AttributeError('Failed to build url. You should check custom routing converter.')

            methods = ', '.join(refine_methods(rule.methods))
            url = unquote(url_for(rule.endpoint, **arguments).replace('http://localhost', ''))

            # replace random keys generated above with argument name
            for arg_name, arg_value in arguments.items():
                url = url.replace(arg_value, '[{}]'.format(arg_name))
                url = re.sub(r'', '', url)

            api = {
                'endpoint': rule.endpoint,
                'methods': methods,
                'url': url,
            }

            if api['endpoint'].split('.')[-1] == 'static' or api['endpoint'].startswith('admin.'):
                continue
            apis.append(api)

    return apis


def is_root_endpoint(endpoint):
    if endpoint.find('.') == -1:
        return True
    return False


def create_directory(apis):
    if not os.path.isdir(doc_dir):
        verbose_message(f'Create {doc_dir} folder')
        os.makedirs(doc_dir, exist_ok=True)
    bps = set()
    for api in apis:
        if is_root_endpoint(api['endpoint']):
            api['bp'] = ''
        else:
            bp = api['endpoint'].split('.')[0]
            bps.add(bp)
            api['bp'] = bp
    for bp in bps:
        if not os.path.isdir(f'{doc_dir}/{bp}'):
            verbose_message(f'Create {doc_dir}/{bp} folder')
            os.mkdir(f'{doc_dir}/{bp}')


def create_doc(apis):
    for api in apis:
        filename = '/'.join(api['endpoint'].split('.'))
        path = os.path.join(doc_dir, filename + '.md')
        if not os.path.exists(path):
            verbose_message(f'Create {path}')
            with open(path, 'wt') as fp:
                fp.write(markdown_template(api))
        api['doc_path'] = path


def markdown_template(api):
    return md_template.format(endpoint=api['endpoint'],
                              url=api['url'],
                              methods=api['methods']
                              )


def readme_template(apis):
    contents = readme_header_template.format(project_name=project_name)
    bps = defaultdict(lambda: [])
    for api in apis:
        bps[api['bp']].append(api)
    bps = sorted(bps.items(), key=lambda kv: kv[0])  # ((bp, router), ...)
    for bp, routers in bps:
        contents += readme_bp_name_template.format(bp_name=bp.capitalize() or '-')
        routers = sorted(routers, key=lambda k: k['url'])
        for api in routers:
            contents += readme_link_template.format(endpoint=api['endpoint'],
                                                    doc_path=api['doc_path'].replace(doc_dir + '/', ''),
                                                    methods=api['methods'],
                                                    url=api['url'])
    return contents


def create_readme(apis):
    readme_path = os.path.join(doc_dir, 'readme.md')
    with open(readme_path, 'wt') as fp:
        fp.write(readme_template(apis))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('project', type=str, help='Project name')
    parser.add_argument('app', type=str, help='Directory or script of flask app instance')
    parser.add_argument('doc_dir', type=str, help='Api doc directory')
    parser.add_argument('-v', '--verbosity', action='store_true')
    parser.add_argument('-a', '--app_name', help='app_name = Flask(__name__)', default='app')
    args = parser.parse_args()

    project_name = args.project
    app_name = args.app_name

    app_dir = args.app
    app_dir = app_dir[:-1] if app_dir.endswith('/') else app_dir
    if not app_dir.startswith('/'):  # relative
        app_dir = os.path.abspath(os.path.join(os.getcwd(), app_dir))

    proj_file = None
    if app_dir.endswith('.py'):
        temp = app_dir.rsplit('/', 2)
        if app_dir.endswith('__init__.py'):
            # temp == [path/to/proj-folder, proj, __init__.py]
            app_path, proj_file = temp[0], temp[1]
        else:
            # temp == [path/to/proj-folder, proj, script.py]
            app_path, proj_file = temp[0] + '/' + temp[1], temp[2][:-3]
    else:
        temp = app_dir.rsplit('/', 1)
        app_path, proj_file = temp[0], temp[1]

    doc_dir = args.doc_dir
    doc_dir = doc_dir[:-1] if doc_dir.endswith('/') else doc_dir
    if not doc_dir.startswith('/'):  # relative
        doc_dir = os.path.abspath(os.path.join(os.getcwd(), doc_dir))
    os.makedirs(doc_dir, exist_ok=True)  # mkdir -p doc_dir

    verbosity = args.verbosity

    print('project  : ', project_name)
    print('proj_file: ', proj_file)
    print('app path : ', app_path)
    print('doc      : ', doc_dir)
    print('app_name : ', app_name)

    sys.path.append(app_path)
    app_module = importlib.import_module(proj_file)
    app = getattr(app_module, app_name)
    import flask

    if type(app) != flask.Flask:
        raise TypeError('app is not flask.Flask')

    app.config['SERVER_NAME'] = 'localhost'

    apis = list_routes(app=app)

    create_directory(apis)
    create_doc(apis)
    create_readme(apis)
