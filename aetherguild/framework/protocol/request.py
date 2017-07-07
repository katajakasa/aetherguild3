
class Request(object):
    def __init__(self, db, session, message, stream, route):
        self.db = db
        self.session = session
        self.message = message
        self.stream = stream
        self.route = route
