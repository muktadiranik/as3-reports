from django.core.management.base import BaseCommand, CommandError
# from as3.core.models import Users
from django.contrib.auth.management.commands import createsuperuser

class Command(createsuperuser.Command):
    help = 'Create New superuser'

    def add_arguments(self, parser):
        parser.add_argument('--username', dest='username', type=str, help='Specifies the username for the superuser.')
        parser.add_argument('--email', dest='email', type=str, help='Specifies the email for the superuser.')
        parser.add_argument('--password', dest='password', help='Specifies the password for the superuser.', type = str)
        # super(Command, self).add_arguments(parser)
        
    def handle(self, *args, **options):
        try:
            password = options.get('password')
            username = options.get('username')
            email = options.get('email')
            if not password or  not username or not email:
                raise CommandError("--username is required if specifying --password")
            
            user = self.UserModel(
                username = options['username'].strip(),
                email = options['email'].strip(),
            )
            user.set_password(options['password'].strip())
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print("Superuser created successfully!")
        except Exception as e:
            print("Error while creating super user")