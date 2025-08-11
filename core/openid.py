from core import settings
import urllib.parse


def logout(request):
    logout_request = (
        f"{settings.OIDC_OP_LOGOUT_ENDPOINT}?"
        f"{urllib.parse.urlencode({
            'client_id': settings.OIDC_RP_CLIENT_ID,
            'post_logout_redirect_uri': request.build_absolute_uri(settings.POST_LOGOUT_URL)
            })}"
    )

    return logout_request
