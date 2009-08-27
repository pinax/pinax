from django.db import connection, transaction


qn = connection.ops.quote_name


def generate_next_scoped_id(content_object, scoped_id_model):
    """
    generates an ID unique to a content_object scoped in a group (if it has
    one).
    """
    
    kwargs = {}
    if content_object.group:
        kwargs.update({
            "content_type": content_object.content_type,
            "object_id": content_object.object_id,
        })
    get_or_create = scoped_id_model._default_manager.get_or_create
    scoped_id, created = get_or_create(**dict(kwargs, **{
        "defaults": {
            "scoped_number": 1,
        }
    }))
    if not created:
        sql = """
        UPDATE %(table_name)s
        SET scoped_number = scoped_number + 1
        """ % {"table_name": qn(scoped_id_model._meta.db_table)}
        if content_object.group:
            sql += """
            WHERE
                content_type_id = %(content_type_id)s AND
                object_id = %(object_id)s
            """ % {
                "content_type_id": kwargs["content_type"].pk,
                "object_id": kwargs["object_id"],
            }
        try:
            try:
                transaction.enter_transaction_management()
                transaction.managed(True)
                
                cursor = connection.cursor()
                cursor.execute(sql)
                
                # we modified data, mark dirty
                transaction.set_dirty()
                
                scoped_id = scoped_id_model._default_manager.get(pk=scoped_id.pk)
                transaction.commit()
            except:
                transaction.rollback()
                raise
        finally:
            transaction.leave_transaction_management()
            
    return scoped_id.scoped_number
