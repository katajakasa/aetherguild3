from . import BaseCommand


class CreateUser(BaseCommand):
    description = "Create a new user account"

    @staticmethod
    def get_args(args):
        args.add_argument('-u', '--username', type=str, help="Login username")
        args.add_argument('-e', '--email', type=str, help="Email address")
        args.add_argument('-a', '--alias', type=str, help="User alias")
        args.add_argument('-g', '--groups', type=str, help="User groups")

    async def on_run(self, args, app):
        db = app['db']
        await db.execute()
