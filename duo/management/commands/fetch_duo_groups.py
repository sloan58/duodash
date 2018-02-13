import duo_client
from django.core.management.base import BaseCommand, CommandError

from duo.models import Group


class Command(BaseCommand):

    help = 'Fetch all Duo Groups via Admin API'

    def handle(self, *args, **options):

        # Get the Duo Admin API parameters
        # ikey = input(self.style.SUCCESS('Please enter Admin API integration key ("DI..."): '))
        # skey = input(self.style.SUCCESS('Please enter the secret key: '))
        # host = input(self.style.SUCCESS('Please enter the API hostname ("api-....duosecurity.com"): '))

        ikey = '***REMOVED***'
        skey = '***REMOVED***'
        host = '***REMOVED***'

        # Create the Duo Admin API Client Object
        admin_api = duo_client.Admin(
            ikey, skey, host
        )

        self.stdout.write(self.style.WARNING('[-]') + ' Creating Duo Admin Client and querying the API...')

        # Fetch all Duo Groups
        try:
            groups = admin_api.get_groups()
        except RuntimeError as e:
            self.stdout.write(self.style.ERROR('[!] %s (%s)' % (e, type(e))))
            exit()

        self.stdout.write(self.style.WARNING('[-]') + ' Found %s Duo Groups to store locally' % len(groups))

        # Iterate the Groups for insert/update
        for group in groups:

            # Create a dictionary for the Duo Group
            duo_group = {
                'group_id': group['group_id'],
                'name': group['name'],
                'desc': group['desc'],
                'status': group['status'],
                'mobile_otp_enabled': group['mobile_otp_enabled'],
                'push_enabled': group['push_enabled'],
                'sms_enabled': group['sms_enabled'],
                'voice_enabled': group['voice_enabled'],
            }

            # Call get_or_create with the duo_group dictionary
            try:
                instance, created = Group.objects.get_or_create(group_id=group['group_id'], defaults=duo_group)
            except Exception as e:
                self.stdout.write(self.style.ERROR('[!] %s (%s)' % (e, type(e))))
                continue

            # If the object was not 'created', then it already existed.  Update the model as needed
            if not created:
                for attr, value in duo_group.items():
                    setattr(instance, attr, value)

                # Save the updates
                try:
                    instance.save()
                except Exception as e:
                    self.stdout.write(self.style.ERROR('[!] %s (%s)' % (e, type(e))))
                    continue

        self.stdout.write(self.style.SUCCESS('[√]') + ' Finished!')
