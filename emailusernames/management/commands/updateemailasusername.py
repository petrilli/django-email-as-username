import sys
from django.db import IntegrityError, transaction
from django.contrib.auth.models import User
from django.core.management.base import NoArgsCommand
from emailusernames.utils import _email_to_username

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """Upgrade the existing User table to be usable by django-email-as-username.

        This is specifically designed for versions 1.3 and above of the package."""

        title = "Upgrading User table for django-email-as-username"
        sys.stdout.write("=====\n" + title + "\n=====\n")
        sys.stdout.flush()

        total = User.objects.count()
        failed = 0

        for user in User.objects.all():
            user.username = _email_to_username(user.email)
            try:
                sid = transaction.savepoint()
                user.save()
                transaction.savepoint_commit(sid)
            except IntegrityError:
                failed += 1
                sys.stdout.write(
                    "Could not convert user with username '%s' because the email "
                    "<%s> is already taken.\n" % (user.username, user.email)
                    )
                sys.stdout.flush()
                transaction.savepoint_rollback(sid)

        sys.stdout.write("Converted %d of %d users (%d failed).\n" % (total - failed, total, failed))
