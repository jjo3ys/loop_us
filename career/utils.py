from django.db.utils import IntegrityError

def delete_tag(tag_obj):
    for tag in tag_obj:
        tag.tag.count = tag.tag.count-1
        if tag.tag.count == 0:
            try:
                tag.tag.delete()
            except IntegrityError:
                pass
        else:
            tag.tag.save()