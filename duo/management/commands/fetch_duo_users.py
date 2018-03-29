import datetime

import duo_client
import pytz
from django.conf import settings
from django.core.management.base import BaseCommand


from duo.models import User, Phone, Group, Token


class Command(BaseCommand):

    help = 'Fetch all Duo Users via Admin API'

    def handle(self, *args, **options):

        # Get all the users from the Duo API
        users = self.call_duo_api()

        # Remove local Duo User accounts no longer returned via API
        self.remove_stale_accounts(self, users)

        self.stdout.write(
            self.style.WARNING('[-]') +
            ' Processing API Data for local storage'
        )

        # Process the API data
        for user in users:

            self.process_user(user)

        self.stdout.write(self.style.SUCCESS('[√]') + ' Finished!')
                    
    def call_duo_api(self):
        # Get the Duo Admin API parameters
        ikey = settings.DUO_IKEY
        skey = settings.DUO_SKEY
        host = settings.DUO_HOST

        # Create the Duo Admin API Client Object
        admin_api = duo_client.Admin(
            ikey, skey, host
        )

        self.stdout.write(
            self.style.WARNING('[-]') +
            ' Creating Duo Admin Client and querying the API...')

        # Fetch all Duo Users
        try:
            users = admin_api.get_users()
        except RuntimeError as e:
            self.stdout.write(self.style.ERROR('[!] %s (%s)' % (e, type(e))))
            exit()

        self.stdout.write(
            self.style.WARNING('[-]') +
            ' Found %s Duo Users to store locally' % len(users)
        )

        return users

    @staticmethod
    def remove_stale_accounts(self, users):
        """Remove stale local User accounts.

        These are accounts that exist in the local database
        but are not returned from the API

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
        self.stdout.write(
            self.style.WARNING('[-]') +
            ' Removing stale local User accounts (%s)' % len(stales)
            )

        for stale in stales:
            User.objects.filter(user_id=stale).first().delete()

    def process_user(self, user):

        # Just picking a timezone since we have to....
        timezone = pytz.timezone("America/New_York")

        # Django model DateTimeField does not play nice
        # with Unix Timestamps.  Check to see if it exists
        # and convert it to a Datetime format with timezone
        if user['last_login'] is not None:
            last_login = datetime.datetime.fromtimestamp(
                user['last_login'],
                tz=timezone
            )
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
            user_instance, created = User.objects.get_or_create(
                user_id=user['user_id'],
                defaults=duo_user
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR('[!] %s (%s)' % (e, type(e)))
            )
            return False

        # If the object was not 'created', then it already existed.
        if not created:
            for attr, value in duo_user.items():
                setattr(user_instance, attr, value)

            # Save the updates
            try:
                user_instance.save()
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR('[!] %s (%s)' % (e, type(e)))
                )
                return False

        # Associate User Tokens
        if len(user['tokens']):

            self.process_user_tokens(user, user_instance)

        # Associate User Groups
        if len(user['groups']):

            self.process_user_groups(user, user_instance)

        # Associate User Phones

            self.process_user_phones(user, user_instance)

    def process_user_tokens(self, user, user_instance):

        for token in user['tokens']:

            # Call get_or_create with the token dictionary
            try:
                token_instance, created = Token.objects.get_or_create(
                    serial=token['serial'],
                    defaults=token
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR('[!] %s (%s)' % (e, type(e)))
                )
                return

            # If the object was not 'created', then it already existed.
            if not created:
                for attr, value in token.items():
                    setattr(token_instance, attr, value)

                # Save the updates
                try:
                    token_instance.save()
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR('[!] %s (%s)' % (e, type(e)))
                    )
                    return

            # Save the Duo Token/User Many to Many Relationship
            token_instance.users.add(user_instance)

    @staticmethod
    def process_user_groups(user, user_instance):

        for group in user['groups']:
            group_instance = Group.objects.filter(group_id=group['group_id']).first()
            group_instance.users.add(user_instance)

    def process_user_phones(self, user, user_instance):

        for phone in user['phones']:

            # Call get_or_create with the phone dictionary
            try:
                phone_instance, created = Phone.objects.get_or_create(
                    phone_id=phone['phone_id'],
                    name=phone['name'],
                    number=phone['number'],
                    extension=phone['extension'],
                    type=phone['type'],
                    platform=phone['platform'],
                    postdelay=phone['postdelay'],
                    predelay=phone['predelay'],
                    sms_passcodes_sent=phone['sms_passcodes_sent'],
                    activated=phone['activated']
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR('[!] %s (%s)' % (e, type(e)))
                )
                return

            # If the object was not 'created', then it already existed.
            if not created:
                for attr, value in phone.items():
                    setattr(phone_instance, attr, value)

                # Save the updates
                try:
                    phone_instance.save()
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR('[!] %s (%s)' % (e, type(e)))
                    )
                    return

            # Save the Duo Token/User Many to Many Relationship
            phone_instance.users.add(user_instance)
