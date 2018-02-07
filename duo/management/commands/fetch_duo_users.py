import datetime
import duo_client
from django.core.management.base import BaseCommand, CommandError

from duo.models import User


class Command(BaseCommand):

    help = 'Fetch all Duo users via Admin API'

    def handle(self, *args, **options):

        # Get the Duo Admin API parameters
        ikey = input(self.style.SUCCESS('Please enter Admin API integration key ("DI..."): '))
        skey = input(self.style.SUCCESS('Please enter the secret key: '))
        host = input(self.style.SUCCESS('Please enter the API hostname ("api-....duosecurity.com"): '))

        # Create the Duo Admin API Client Object
        admin_api = duo_client.Admin(
            ikey, skey, host
        )

        # Fetch all Duo Users
        try:
            users = admin_api.get_users()
        except RuntimeError as e:
            self.stdout.write(self.style.ERROR('%s (%s)' % (e, type(e))))
            exit()

        self.stdout.write("[+] Found %s Duo Users" % len(users))

        # Iterate the Users for insert/update
        for user in users:

            # Create a dictionary for the Duo User
            duo_user = {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'status': user['status'],
                'realname': user['realname'],
                'notes': user['notes']
                # TODO: handle unix timestamps better
                # 'last_login':datetime.datetime.fromtimestamp(int(user['last_login']))
            }

            try:
                instance, created = User.objects.get_or_create(user_id=user['user_id'], defaults=duo_user)
            except Exception as e:
                self.stdout.write(self.style.ERROR('%s (%s)' % (e, type(e))))
                continue

            if not created:
                for attr, value in duo_user.items():
                    setattr(instance, attr, value)
                instance.save()

