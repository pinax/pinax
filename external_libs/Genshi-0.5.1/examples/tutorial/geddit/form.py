from formencode import Schema, validators


class LinkForm(Schema):
    username = validators.UnicodeString(not_empty=True)
    url = validators.URL(not_empty=True, add_http=True, check_exists=False)
    title = validators.UnicodeString(not_empty=True)


class CommentForm(Schema):
    username = validators.UnicodeString(not_empty=True)
    content = validators.UnicodeString(not_empty=True)
