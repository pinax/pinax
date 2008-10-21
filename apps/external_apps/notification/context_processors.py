from notification.models import Notice

def notification(request):
    if request.user.is_authenticated():
        return {'notice_unseen_count': Notice.objects.unseen_count_for(request.user),}
    else:
        return {}
