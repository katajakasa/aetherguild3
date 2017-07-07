
class Route(object):
    def __init__(self, handler, schema=None):
        self.handler = handler
        self.schema = {
            'message': {
                'type': 'dict',
                'required': True,
                'schema': schema
            }
        }
