import random

from django.contrib.auth.models import User

from notification.models import NoticeType, NoticeSetting, ObservedItem

def generate():
    for user in User.objects.all():
        for notice_type in NoticeType.objects.all():
            en = random.random() <= 0.1
            notice_setting = NoticeSetting.objects.create(
                user=user,
                notice_type=notice_type,
                medium="1",
                send=en
            )
            print "%sabled notices for %s on %s" % (en and 'En' or 'Dis',
                user, notice_type)

if __name__ == '__main__':
    generate()