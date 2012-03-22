from django.contrib.auth.models import User
from emailusernames.utils import get_user

MASQUERADE_SEPARATOR = '/'

class EmailAuthBackend(object):
    """Allow users to log in with their email address.

    It also allows a staff member to impersonate another user. This is done
    by parsing the password field differently. If the user is unable to be
    authenticated initially, the password field is split on a '/', and if found,
    then the field will become a username and password combination to use."""

    supports_inactive_user = False
    supports_anonymous_user = False
    supports_object_permissions = False

    def authenticate(self, email=None, password=None):
        try:
            proposed_user = get_user(email)
            if proposed_user.check_password(password):
                proposed_user.backend = "%s.%s" % (self.__module__, self.__class__.__name__)
                return proposed_user
            else:
                # See if we can masquerade or not
                if MASQUERADE_SEPARATOR in password:
                    (masked_email, masked_password) = password.split(MASQUERADE_SEPARATOR, 1)
                    real_user = self.authenticate(email=masked_email, password=masked_password)
                    if real_user and real_user.is_staff:
                        return proposed_user
                return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
