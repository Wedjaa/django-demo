import base64, json
from typing import Dict

def _decode_jwt(token: str) -> Dict:
    if not token or '.' not in token:
        return {}
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return {}
        payload = parts[1] + '=' * (-len(parts[1]) % 4)
        data = base64.urlsafe_b64decode(payload.encode('utf-8'))
        return json.loads(data.decode('utf-8'))
    except Exception:
        return {}

def user_claims(request):
    id_token = request.session.get('oidc_id_token') or request.session.get('OIDC_ID_TOKEN')
    claims = _decode_jwt(id_token) if id_token else {}
    picture = claims.get('picture')
    
    # Extract roles for global access
    roles = claims.get('django/roles') or claims.get('django_roles') or []
    if isinstance(roles, str):
        if ',' in roles:
            roles = [r.strip() for r in roles.split(',') if r.strip()]
        else:
            roles = [roles]
    if not isinstance(roles, (list, tuple)):
        roles = []
    
    # Store roles in user object for django-rules
    if request.user.is_authenticated:
        request.user._oidc_roles = roles
    
    return {
        'oidc_id_claims': claims,
        'oidc_user_picture': picture,
        'user_roles': roles,
    }
