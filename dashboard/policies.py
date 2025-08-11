# Python 3.10 not happy with these operators
# type: ignore
import rules
from rules.predicates import predicate
from .models.djangouser import DjangoUser

def get_user_roles(user: DjangoUser):
    """Extract roles from user's OIDC session"""
    print(f"Getting roles for user: {user}")
    if not user or not user.is_authenticated:
        print("User is not authenticated or does not exist.")
        return []

    # Try to get roles from session - this requires accessing the request
    # For now, we'll add them as user attributes when they log in
    roles = user.roles
    print(f"Extracted roles: {roles}")
    return roles


# Predicates for checking user roles
@predicate
def is_admin(user: DjangoUser):
    """Check if user has admin role"""
    print(f"Checking if user {user.username} is admin")
    roles = get_user_roles(user)
    return "admin" in roles


@predicate
def is_reader(user: DjangoUser):
    """Check if user has reader role"""
    print(f"Checking if user {user.username} is reader")
    roles = get_user_roles(user)
    return "reader" in roles


@predicate
def is_trader(user: DjangoUser):
    """Check if user has trader role"""
    print(f"Checking if user {user.username} is trader")
    roles = get_user_roles(user)
    return "trader" in roles


@predicate
def is_confirmer(user: DjangoUser):
    """Check if user has confirm role"""
    print(f"Checking if user {user.username} is confirmer")
    roles = get_user_roles(user)
    print(f"Roles for user {user.username}: {roles}")
    return "confirms" in roles


@predicate
def is_approver(user: DjangoUser):
    """Check if user has approver role"""
    print(f"Checking if user {user.username} is approver")
    roles = get_user_roles(user)
    return "approver" in roles


@predicate
def is_trade_creator(user: DjangoUser, trade):
    """Check if user created the trade"""
    print(f"Checking if user {user.username} is creator of trade {trade}")
    return trade and trade.created_by == user


@predicate
def is_trade_pending(user: DjangoUser, trade):
    """Check if trade is in pending status"""
    return trade and trade.status == "PENDING"


@predicate
def is_trade_confirmed(user: DjangoUser, trade):
    """Check if trade is in confirmed status"""
    return trade and trade.status == "CONFIRMED"


@predicate
def is_trade_not_confirmed(user: DjangoUser, trade):
    """Check if trade is not yet confirmed"""
    return trade and trade.status in ["PENDING"]

# View permissions
rules.permissions.add_perm("trade.view_trade", is_admin | is_reader | is_trader | is_confirmer | is_approver)

# List permissions
rules.permissions.add_perm(
    "trade.view_tradelist",
    is_admin | is_reader | is_trader | is_confirmer | is_approver,
)

# Create permissions
rules.permissions.add_perm("trade.create_trade", is_admin | is_trader)

# Delete permissions - traders can delete their own trades if not confirmed
rules.permissions.add_perm(
    "trade.delete_trade",
    is_admin | (is_trader & is_trade_creator & is_trade_not_confirmed),
)

# Change permissions - only admin for now
rules.permissions.add_perm("trade.change_trade", is_admin)

# Confirm permissions - confirmers can confirm pending trades or move confirmed back to pending
rules.permissions.add_perm(
    "trade.confirm_trade",
    is_admin | (is_confirmer & (is_trade_pending | is_trade_confirmed)),
)

# Approve permissions - approvers can approve confirmed trades
rules.permissions.add_perm(
    "trade.approve_trade", is_admin | (is_approver & is_trade_confirmed)
)

# Reject permissions - approvers can reject confirmed trades
rules.permissions.add_perm(
    "trade.reject_trade", is_admin | (is_approver & is_trade_confirmed)
)

# Move back to pending - confirmers can move confirmed trades back to pending
rules.permissions.add_perm(
    "trade.unconfirm_trade", is_admin | (is_confirmer & is_trade_confirmed)
)
