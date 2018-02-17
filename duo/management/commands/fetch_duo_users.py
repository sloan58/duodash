import datetime

import duo_client
import pytz
from django.conf import settings
from django.core.management.base import BaseCommand

from duo.models import Token
from duo.models import User


class Command(BaseCommand):

    help = 'Fetch all Duo Users via Admin API'

    def handle(self, *args, **options):

        # Get the Duo Admin API parameters
        ikey = settings.DUO_IKEY
        skey = settings.DUO_SKEY
        host = settings.DUO_HOST

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

        # Remove local Duo User accounts that are no longer returned from the API
        self.remove_stale_accounts(self, users)

        # Just picking a timezone since we have to....
        timezone = pytz.timezone("America/New_York")

        # Iterate the Users for insert/update
        for user in users:

            # TODO: Start breaking these processes into smaller methods
            
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
                user_instance, created = User.objects.get_or_create(user_id=user['user_id'], defaults=duo_user)
            except Exception as e:
                self.stdout.write(self.style.ERROR('[!] %s (%s)' % (e, type(e))))
                continue

            # If the object was not 'created', then it already existed.  Update the model as needed
            if not created:
                for attr, value in duo_user.items():
                    setattr(user_instance, attr, value)

                # Save the updates
                try:
                    user_instance.save()
                except Exception as e:
                    self.stdout.write(self.style.ERROR('[!] %s (%s)' % (e, type(e))))
                    continue

            if len(user['tokens']):

                for token in user['tokens']:

                    # Call get_or_create with the token dictionary
                    try:
                        token_instance, created = Token.objects.get_or_create(serial=token['serial'], defaults=token)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR('[!] %s (%s)' % (e, type(e))))
                        continue

                    # If the object was not 'created', then it already existed.  Update the model as needed
                    if not created:
                        for attr, value in duo_user.items():
                            setattr(token_instance, attr, value)

                        # Save the updates
                        try:
                            token_instance.save()
                        except Exception as e:
                            self.stdout.write(self.style.ERROR('[!] %s (%s)' % (e, type(e))))
                            continue

                    # Save the Duo Token/User Many to Many Relationship
                    token_instance.users.add(user_instance)

        self.stdout.write(self.style.SUCCESS('[√]') + ' Finished!')

    @staticmethod
    def remove_stale_accounts(self, users):
        """Remove stale local User accounts.

        These are accounts that exist in the local database but are not returned from the API

        :param self:
        :param users:
        """
        # All of the user_id's from the recently fetched Duo API
        duo_user_id_list = [o['user_id'] for o in users]

        # All of the local user user_id's
        local_users = User.objects.values_list('user_id', flat=True)

        # The difference between local users and duo_users
        stales = list(set(local_users) - set(duo_user_id_list))

        # Delete the local users that don't exist in the Duo database
        self.stdout.write(self.style.WARNING('[-]') + ' Removing stale local User accounts (%s)' % len(stales))
        for stale in stales:
            User.objects.filter(user_id=stale).first().delete()

