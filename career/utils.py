from django.db.utils import IntegrityError
# 태그 모델에서 count 변화 function
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

POST_PREFETCH_LIST = ["contents_image", "contents_link", "contents_file", "comments__cocomments", "post_like", "post_tag"]
POST_SELECTE_LIST = ["career"]