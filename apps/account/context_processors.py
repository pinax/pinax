
from account.models import Account, AnonymousAccount

def openid(request):
    return {'openid': request.openid}

def account(request):
    if request.user.is_authenticated():
        try:
            account = Account._default_manager.get(user=request.user)
        except Account.DoesNotExist:
            account = AnonymousAccount(request)
    else:
        account = AnonymousAccount(request)
    return {'account': account}
