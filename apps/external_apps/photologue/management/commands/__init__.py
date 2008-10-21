from photologue.models import PhotoSize

def get_response(msg, func=int, default=None):
    while True:
        resp = raw_input(msg)
        if not resp and default is not None:
            return default
        try:
            return func(resp)
        except:
            print 'Invalid input.'

def create_photosize(name, width=0, height=0, crop=False, pre_cache=False, increment_count=False):
    try:
        size = PhotoSize.objects.get(name=name)
        exists = True
    except PhotoSize.DoesNotExist:
        size = PhotoSize(name=name)
        exists = False
    if exists:
        msg = 'A "%s" photo size already exists. Do you want to replace it? (yes, no):' % name
        if not get_response(msg, lambda inp: inp == 'yes', False):
            return
    print '\nWe will now define the "%s" photo size:\n' % size
    w = get_response('Width (in pixels):', lambda inp: int(inp), width)
    h = get_response('Height (in pixels):', lambda inp: int(inp), height)
    c = get_response('Crop to fit? (yes, no):', lambda inp: inp == 'yes', crop)
    p = get_response('Pre-cache? (yes, no):', lambda inp: inp == 'yes', pre_cache)
    i = get_response('Increment count? (yes, no):', lambda inp: inp == 'yes', increment_count)
    size.width = w
    size.height = h
    size.crop = c
    size.pre_cache = p
    size.increment_count = i
    size.save()
    print '\nA "%s" photo size has been created.\n' % name
    return size
