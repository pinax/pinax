from django.contrib.auth.models import User

from notification.models import NoticeQueueBatch, send_now

try:
    import cPickle as pickle
except ImportError:
    import pickle

def generate():
    print "Sending 10% of the stored notifications"
    num = NoticeQueueBatch.objects.count()
    users = dict([(str(u.id), u) for u in User.objects.all()])
    print "Unpickling batch data"
    batches = map(
        lambda data: pickle.loads(data.decode("base64"))[0],
        NoticeQueueBatch.objects.order_by('?').values_list('pickled_data',
            flat=True)[:num / 10]
    )
    print "Unpickled batch data"
    NoticeQueueBatch.objects.all().delete()
    i = 0
    for i, args in enumerate(batches):
        arg_list = list(args)
        arg_list[0] = [users[str(arg_list[0])]]
        send_now(*arg_list)
    print "%d notifications sent" % (i,)

if __name__ == '__main__':
    generate()