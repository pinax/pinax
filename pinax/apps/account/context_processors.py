from pinax.apps.account.models import Account, AnonymousAccount



def openid(request):
    if hasattr(request, "openid"):
        openid = request.openid
    else:
        openid = None
    return {
        "openid": openid,
    }


def account(request):
    if request.user.is_authenticated():
        try:
            account = Account._default_manager.get(user=request.user)
        except Account.DoesNotExist:
            account = AnonymousAccount(request)
    else:
        account = AnonymousAccount(request)
    return {"account": account}
