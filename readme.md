# Flask REST API Documentation Templates


**This only provides templates. Contents should be written by yourself.**

### Be Careful
- If `some_endpoint.md` is created already, this file would not be updated because of preventing overwrite. 
If you want to update or recreate this doc, just delete it.
- `readme.md` in `doc_dir` will always be changed.
- As I said, you should fill all details about router, args, data, response, error and so on.


### Example
- [example](example/api_doc/readme.md) - used flask blueprint example. (http://flask.pocoo.org/docs/1.0/blueprints/)
    ```
    /home/user/dev/flask_api_doc_templates
    ├── example/
    │   ├── __init__.py
    │   └── views.py
    ```
    `$ python create_api_doc.py example ./example ./example/api_doc -a app`


### Usage
`python create_api_doc.py [-h] [-v] [-a APP_NAME] project app doc_dir`
  
1. `APP_NAME` is variable name of `Flask` instance. Default is 'app'
    ```python
    from flask import Flask
    APP_NAME = Flask(__name__)
    ```
    
2. `project` is only for document header. Not that important.

3. `app` is relative path or absolute path where `__init__.py` that has `Flask` instance is or python script.
     ```
    /home/user/dev/your-project
    ├── your_app/
    │   ├── __init__.py
    ```
    If project structure looks like this above and `Flask` instance is in `__init__.py`,
    `app` is `/home/user/dev/your-project/your_app`
    ```
    /home/user/dev/your-project
    ├── your_app/
    │   ├── __init__.py
    └── runserver.py
    ``` 
    If looks like this and `Flask` instance is in `runserver.py`,
     `app` is `/home/user/dev/your-project/runserver.py`
     
4. `doc_dir` is where documents will be located. Relative or absolute path both are allowed.

5. Because this script import your `Flask app`, load views and blueprints, you should install all requirements that your project use. 
    ```
    $ pip install -r requirements.txt
    $ pip install -r your_project_requirements.txt
    ```

6. Finally
    ```
    $ python create_api_doc.py project_name path/to/app/or/script path/to/doc 
    ```

### Markdown template
 Inspired by https://github.com/jamescooke/restapidocs  
