from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from dashboard.models.djangouser import DjangoUser

class DjangoGroupsAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        email = claims.get("email")
        username = self.get_username(claims)
        user = DjangoUser.manager.create_user(username, email=email, password=None)
        print(f"Creating user: {username} with email: {email}")
        roles = claims.get("django/roles", [])
        print(f"Assigning roles to new user: {roles}")
        user.roles = roles
        user.save()
        return user

    def update_user(self, user, claims):
        roles = claims.get("django/roles", [])
        print(f"Updating roles for user: {roles}")
        user.roles = roles
        user.save()
        return user
