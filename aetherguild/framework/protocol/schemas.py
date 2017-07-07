
base_request = {
    'route': {
        'type': 'string',
        'required': True
    },
    'type': {
        'type': 'string',
        'required': True,
        'allowed': ['open', 'close']
    },
    'stream': {
        'type': 'string',
        'required': True
    },
    'session': {
        'type': 'string',
        'required': False
    },
    'message': {
        'type': 'dict',
        'required': True,
        'allow_unknown': True,
        'schema': {}
    }
}
