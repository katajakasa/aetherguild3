from aetherguild.backend.handlers.auth import login_handler
from aetherguild.backend.schemas.auth import login_request_schema
from aetherguild.framework.web.route import Route


routes = {
    'aether.auth.login': Route(login_handler, login_request_schema)
}
