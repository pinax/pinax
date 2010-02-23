from account import signals

from request_receivers import receivers



signals.account_user_signed_up.connect(receivers.account_user_signed_up)