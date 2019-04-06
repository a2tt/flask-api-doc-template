
readme_header_template = '''
# {project_name} API Doc

## Endpoints

'''
readme_bp_name_template = '''
### {bp_name}  
'''
readme_link_template = '''
* [{endpoint}]({doc_path}) : `{methods}` {url}  
'''

md_template = '''
# {endpoint}

;P

**URL** : `{url}`

**Method** : `{methods}`

**Auth required** : 

**Permissions required** : 

**Data constraints** : 
```json
{{
}}
```

## Success Responses

**Status Code** : ``

**Content** :
```json
{{
}}
```

## Error Responses

**Case** : 

**Status Code** : ``

**Content** : 
```json
{{
  "error": "", 
  "code": ""
}}
```
'''
