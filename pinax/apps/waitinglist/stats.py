from pinax.apps.waitinglist.models import WaitingListEntry


def stats():
    return {
        "waiting_list_entries": WaitingListEntry.objects.count()
    }
