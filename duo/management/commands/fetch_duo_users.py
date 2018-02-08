import pytz
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

        self.stdout.write(self.style.WARNING('[-]') + ' Creating Duo Admin Client and querying the API...')

        # Fetch all Duo Users
        try:
            users = admin_api.get_users()
        except RuntimeError as e:
            self.stdout.write(self.style.ERROR('[!] %s (%s)' % (e, type(e))))
            exit()

        self.stdout.write(self.style.WARNING('[-]') + ' Found %s Duo Users to store locally' % len(users))

        # Just picking a timezone since we have to....
        timezone = pytz.timezone("America/New_York")

        # Iterate the Users for insert/update
        for user in users:

            # Django model DateTimeField does not play nice
            # with Unix Timestamps.  Check to see if it exists
            # and convert it to a Datetime format with timezone
            if user['last_login'] is not None:
                last_login = datetime.datetime.fromtimestamp(user['last_login'], tz=timezone)
            else:
                last_login = None

            # Create a dictionary for the Duo User
            duo_user = {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'status': user['status'],
                'realname': user['realname'],
                'notes': user['notes'],
                'last_login': last_login
            }

            # Call get_or_create with the duo_user dictionary
            try:
                instance, created = User.objects.get_or_create(user_id=user['user_id'], defaults=duo_user)
            except Exception as e:
                self.stdout.write(self.style.ERROR('[!] %s (%s)' % (e, type(e))))
                continue

            # If the object was not 'created', then it already existed.  Update the model as needed
            if not created:
                for attr, value in duo_user.items():
                    setattr(instance, attr, value)

                # Save the updates
                try:
                    instance.save()
                except Exception as e:
                    self.stdout.write(self.style.ERROR('[!] %s (%s)' % (e, type(e))))
                    continue

        self.stdout.write(self.style.SUCCESS('[√]') + ' Finished!')
