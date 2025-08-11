from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
import base64
import json
from .models.trade import Trade
from .forms import TradeForm
from .policies import *  # Import policies for django-rules
from rules.contrib.views import permission_required, objectgetter

@login_required
def home(request):
    return render(request, "dashboard/home.html")


def _decode_jwt(token: str):
    if not token or "." not in token:
        return {}
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        data = base64.urlsafe_b64decode(payload.encode("utf-8"))
        return json.loads(data.decode("utf-8"))
    except Exception:
        return {}


@login_required
def profile(request):
    id_token = request.session.get("oidc_id_token") or request.session.get(
        "OIDC_ID_TOKEN"
    )
    access_token = request.session.get("oidc_access_token") or request.session.get(
        "OIDC_ACCESS_TOKEN"
    )
    refresh_token = request.session.get("oidc_refresh_token") or request.session.get(
        "OIDC_REFRESH_TOKEN"
    )

    id_claims = _decode_jwt(id_token) if id_token else {}
    access_claims = (
        _decode_jwt(access_token)
        if access_token and access_token.count(".") == 2
        else {}
    )

    def _classify(value):
        if isinstance(value, dict):
            return "dict"
        if isinstance(value, (list, tuple)):
            return "list"
        return "scalar"

    # Standard OIDC / common identity claims list
    standard_keys = {
        "sub",
        "iss",
        "aud",
        "exp",
        "iat",
        "auth_time",
        "nonce",
        "acr",
        "amr",
        "azp",
        "at_hash",
        "c_hash",
        "email",
        "email_verified",
        "name",
        "given_name",
        "family_name",
        "middle_name",
        "nickname",
        "preferred_username",
        "profile",
        "picture",
        "website",
        "gender",
        "birthdate",
        "zoneinfo",
        "locale",
        "updated_at",
    }

    standard_claims_items = []
    custom_claims_items = []

    for k, v in id_claims.items():
        item = {"key": k, "type": _classify(v), "value": v}
        if k in standard_keys:
            standard_claims_items.append(item)
        else:
            custom_claims_items.append(item)

    # Extract roles (Okta custom claim name with slash)
    roles = id_claims.get("django/roles") or id_claims.get("django_roles") or []
    if isinstance(roles, str):
        if "," in roles:
            roles = [r.strip() for r in roles.split(",") if r.strip()]
        else:
            roles = [roles]
    if not isinstance(roles, (list, tuple)):
        roles = []

    # Deterministic color mapping for roles
    role_palette = [
        "emerald",
        "cyan",
        "violet",
        "fuchsia",
        "amber",
        "rose",
        "indigo",
        "teal",
        "sky",
        "lime",
    ]
    role_colors = {}
    for r in roles:
        h = sum(ord(c) for c in r)
        color = role_palette[h % len(role_palette)]
        role_colors[r] = color

    # Pre-compute list for template (avoid bracket lookup)
    roles_with_colors = [{"name": r, "color": role_colors[r]} for r in roles]

    context = {
        "id_token": id_token,
        "access_token": access_token,
        "refresh_token": bool(refresh_token),
        "id_claims": id_claims,
        "access_claims": access_claims,
        "standard_claims_items": standard_claims_items,
        "custom_claims_items": custom_claims_items,
        "user_roles": roles,
        "role_colors": role_colors,
        "roles_with_colors": roles_with_colors,
    }
    return render(request, "dashboard/profile.html", context)


@login_required
def admin_panel(request):
    """
    Admin panel view. Uses django-rules permission checking.
    """
    # Check permission using django-rules
    if not request.user.has_perm("dashboard.admin_access"):
        raise PermissionDenied("You don't have permission to access the admin panel")

    # Get admin-specific data
    id_token = request.session.get("oidc_id_token") or request.session.get(
        "OIDC_ID_TOKEN"
    )
    id_claims = _decode_jwt(id_token) if id_token else {}

    context = {
        "user_roles": request.user.roles,
        "id_claims": id_claims,
        "admin_info": {
            "total_claims": len(id_claims),
            "has_email_verified": id_claims.get("email_verified", False),
            "token_issuer": id_claims.get("iss", "Unknown"),
            "token_audience": id_claims.get("aud", "Unknown"),
        },
    }
    return render(request, "dashboard/admin.html", context)


@login_required
def trades_list(request):
    """
    View for listing trades. Uses django-rules for permission checking.
    """
    if not request.user.has_perm("trade.view_tradelist"):
        raise PermissionDenied("You don't have permission to list trades")

    # Get all trades
    trades = Trade.objects.all()

    # Filter by status if requested
    status_filter = request.GET.get("status")
    if status_filter and status_filter in [
        "PENDING",
        "CONFIRMED",
        "APPROVED",
        "REJECTED",
    ]:
        trades = trades.filter(status=status_filter)

    # Pagination
    paginator = Paginator(trades, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Determine user permissions using django-rules
    can_create = request.user.has_perm("trade.add_trade")
    can_confirm = any(
        request.user.has_perm("trade.confirm_trade", trade)
        for trade in page_obj.object_list
    )
    can_approve = any(
        request.user.has_perm("trade.approve_trade", trade)
        for trade in page_obj.object_list
    )

    context = {
        "page_obj": page_obj,
        "trades": page_obj.object_list,
        "user_roles": request.user.roles,
        "can_create": can_create,
        "can_confirm": can_confirm,
        "can_approve": can_approve,
        "status_filter": status_filter,
        "total_trades": Trade.objects.count(),
        "pending_trades": Trade.objects.filter(status="PENDING").count(),
        "confirmed_trades": Trade.objects.filter(status="CONFIRMED").count(),
        "approved_trades": Trade.objects.filter(status="APPROVED").count(),
    }
    return render(request, "dashboard/trades.html", context)


@permission_required('trade.create_trade', raise_exception=True)
def trade_create(request):
    """
    Create a new trade. Uses django-rules permission checking.
    """
    # Check permission using django-rules
    if not request.user.has_perm("trade.add_trade"):
        raise PermissionDenied("You don't have permission to create trades")

    if request.method == "POST":
        form = TradeForm(request.POST)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.created_by = request.user
            trade.save()
            messages.success(request, f"Trade created successfully: {trade}")
            return redirect("dashboard:trades")
    else:
        form = TradeForm()

    context = {
        "form": form,
        "action": "Create",
    }
    return render(request, "dashboard/trade_form.html", context)




@permission_required('trade.confirm_trade', fn=objectgetter(Trade, 'trade_id'), raise_exception=True)
def trade_confirm(request, trade_id):
    """
    Confirm a trade. Uses django-rules permission checking.
    """
    trade = get_object_or_404(Trade, id=trade_id)

    if request.method == "POST":
        action = request.POST.get("action", "confirm")

        if action == "confirm" and trade.can_be_confirmed:
            trade.status = "CONFIRMED"
            trade.confirmed_by = request.user
            trade.confirmed_at = timezone.now()
            trade.save()
            messages.success(request, f"Trade confirmed successfully: {trade}")
        elif action == "unconfirm" and trade.can_be_approved:
            # Move confirmed trade back to pending
            trade.status = "PENDING"
            trade.confirmed_by = None
            trade.confirmed_at = None
            trade.save()
            messages.success(request, f"Trade moved back to pending: {trade}")
        else:
            messages.error(
                request, f"Cannot perform this action on trade in {trade.status} status"
            )

        return redirect("dashboard:trades")

    context = {
        "trade": trade,
        "action": "Confirm",
        "can_unconfirm": trade.status == "CONFIRMED",
    }
    return render(request, "dashboard/trade_action.html", context)


@permission_required('trade.approve_trade', fn=objectgetter(Trade, 'trade_id'), raise_exception=True)
def trade_approve(request, trade_id):
    """
    Approve a trade. Uses django-rules permission checking.
    """
    trade = get_object_or_404(Trade, id=trade_id)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "approve":
            trade.status = "APPROVED"
            trade.approved_by = request.user
            trade.approved_at = timezone.now()
            messages.success(request, f"Trade approved successfully: {trade}")
        elif action == "reject":
            trade.status = "REJECTED"
            messages.warning(request, f"Trade rejected: {trade}")
        else:
            messages.error(request, "Invalid action")
            return redirect("dashboard:trades")

        trade.save()
        return redirect("dashboard:trades")

    context = {
        "trade": trade,
        "action": "Approve",
    }
    return render(request, "dashboard/trade_action.html", context)


@permission_required('trade.view_trade', fn=objectgetter(Trade, 'trade_id'), raise_exception=True)
def trade_detail(request, trade_id):
    """
    View trade details. Uses django-rules permission checking.
    """
    trade = get_object_or_404(Trade, id=trade_id)

    context = {
        "trade": trade,
        "can_confirm": request.user.has_perm("trade.confirm_trade", trade),
        "can_approve": request.user.has_perm("trade.approve_trade", trade),
        "can_delete": request.user.has_perm("trade.delete_trade", trade),
    }
    return render(request, "dashboard/trade_detail.html", context)
