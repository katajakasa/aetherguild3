from aetherguild.framework.app import run_site
from aetherguild.backend.routes import routes
from aetherguild.deprecated.hash import register_hash


if __name__ == '__main__':
    register_hash()
    run_site("aetherguild.settings", routes)
