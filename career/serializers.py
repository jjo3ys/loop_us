from django.db.models import Count, Sum

from rest_framework import serializers

from .models import *

from user.models import Profile, Company
from user.serializers import ProfileListSerializer
from user.utils import PROFILE_SELECT_LIST

from config.settings import COUNT_PER_PAGE

# 간단한 커리어 정보
class CareerInformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career
        fields =["id", "career_name"]

# 썸네일이 포함된 커리어 정보
class CareerWithThumbnailSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Career
        fields = ["id", "career_name", "group", "post_update_date", "is_public",
                  "thumbnail"]
    
    # 커리어 썸네일
    def get_thumbnail(self, obj):
        if obj.thumbnail == 0: return None
        try:
            if obj.tag_company:
                return Company.objects.get(id=obj.thumbnail).logo.url
            else:
                return PostImage.objects.get(id=obj.thumbnail).image.url
        except:
            return None

# 커리어 리스트
class CareerListSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField()
    member  = serializers.SerializerMethodField()
    ratio   = serializers.SerializerMethodField()
    career  = CareerWithThumbnailSerializer(read_only=True)

    class Meta:
        model = CareerUser
        fields = ["user_id", "post_count", "order",
                  "manager", "member", "ratio", 
                  "career"]
    
    # 커리어 방장
    def get_manager(self, obj):
        if obj.is_manager: return obj.user_id
        return CareerUser.objects.get(career_id=obj.career_id, is_manager=True).user_id
    
    # 공유 커리어 멤버
    def get_member(self, obj):
        if obj.career.is_public:
            user_list = CareerUser.objects.select_related(["user__profile__"+_ for _ in PROFILE_SELECT_LIST]).filter(career_id=obj.career_id)
            user_list = list(map(lambda x:x.user.profile, user_list))
            return ProfileListSerializer(user_list, many=True, read_only=True).data
        return None
    
    # 해당 커리어에서 쓴 포스팅 개수 / 전체 포스팅 비율
    def get_ratio(self, obj):
        post_count = Post.objects.filter(user_id=obj.user_id).count()
        if post_count: return round(obj.post_count/post_count, 2)
        else: return 0

# 검색용 태그
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'tag', 'count']

#  태그 리스트
class PostTagSerializer(serializers.ModelSerializer):
    tag       = serializers.SerializerMethodField()
    tag_count = serializers.SerializerMethodField()

    class Meta:
        model = Post_Tag
        fields = ["tag_id", "tag", "tag_count"]
    
    def get_tag(self, obj):
        return obj.tag.tag
    
    def get_tag_count(self, obj):
        return obj.tag.count

# 포스트 이미지
class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ["image"]

# 포스트 업로드 파일
class PostLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLink
        fields = ["link"]

# 포스트 리스트에서 댓글
class CommentSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["content", "like_count",
                  "profile"]

    def get_profile(self, obj):
        return ProfileListSerializer(obj.user.profile, read_only=True).data

# 댓글 리스트
class CommentListSerializer(CommentSerializer):
    class Meta:
        model = Comment
        fields = ["id", "content", "like_count", "date",
                  "profile"]

# 대댓글 리스트
class CocommentListSerializer(CommentSerializer):
    tagged_user = serializers.SerializerMethodField()
    class Meta:
        model = Cocomment
        fields = ["id", "content", "like_count", "date",
                  "profile", "tagged_user"]

    def get_tagged_user(self, obj):
        if obj.tagged:
            return {"real_name":obj.tagged.real_name, "user_id":obj.tagged_id}
        else: return None


# 메인 페이지 포스팅 리스트
class MainPageSerializer(serializers.ModelSerializer):
    profile            = serializers.SerializerMethodField()
    most_liked_comment = serializers.SerializerMethodField()
    file_count         = serializers.SerializerMethodField()
    comment_count      = serializers.SerializerMethodField()
    interest           = serializers.SerializerMethodField()
    post_tag           = PostTagSerializer(many=True, read_only=True)
    contents_image     = PostImageSerializer(many=True, read_only=True)
    contents_link      = PostLinkSerializer(many=True, read_only=True)
    career             = CareerInformSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "user_id", "contents", "date", 
                  "profile", "most_liked_comment", "file_count", "comment_count", "interest"
                  "post_tag", "contents_image", "contents_link", "career"]
    
    # 포스팅 주인 프로필
    def get_profile(self, obj):
        return ProfileListSerializer(obj.user.profile).data
    
    # 포스팅에서 가장 좋아요를 받은 댓글 하나
    def get_most_liked_comment(self, obj):
        if obj.comments.count():
            return CommentSerializer(obj.comments.order_by("-like_count").first(), read_only=True).data
        return []
    
    # 업로드된 파일 개수
    def get_file_count(self, obj):
        return obj.contents_file.count()
    
    # 작성된 댓글, 대댓글 개수
    def get_comment_count(self, obj):
        cocomment_count = Comment.objects.prefetch_related("cocomments").annotate(count=Count("cocomments")).filter(post_id=obj.id).aggregate(c=Sum("count"))
        return obj.comments.count() + cocomment_count["count"]
    
    # 사용자의 좋아요, 북마크 여부 표시
    def get_interest(self, obj):
        if "user_id" in self.context:
            user_id   = self.context.get("user_id")
            like_list = self.context.get("like_list")
            book_list = self.context.get("book_list")

            is_user, is_liked, is_marked = 0, 0, 0
            if user_id == obj.user_id: is_user = 1
            if obj.id in like_list: is_liked = 1
            if obj.id in book_list: is_marked = 1

            return {"is_user":is_user,
                    "is_liked":is_liked,
                    "is_marked":is_marked}
        else: return None

# 포스트
class PostSerializer(MainPageSerializer):
    interest = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "user_id", "contents", "date", 
                  "profile", "file_count", "interest"
                  "post_tag", "contents_image", "contents_link", "career", "comments"]
    
    def get_interest(self, obj):
        user_id = self.context.get("user_id")
        is_user   = obj.user_id == user_id
        is_liked  = Like.objects.filter(user_id=user_id, post_id=obj.id).exists()
        is_marked = BookMark.objects.filter(user_id=user_id, post_id=obj.id).exists()
        return {"is_user":is_user,
                "is_liked":is_liked,
                "is_marked":is_marked}
    
    def get_comments(self, obj):
        comment_obj = obj.comment.all()[:10]
        return CommentListSerializer(comment_obj, many=True, read_only=True).data

# 북마크리스트
class BookMarkListSerializer(MainPageSerializer):
    interst = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "user_id", "contents", "date", 
                  "profile", "last_comment", "file_count", "comment_count", 
                  "post_tag", "contents_image", "contents_link", "career"]
    
    def get_interest(self, obj):
        like_list = self.context.get("like_list")
        if obj.id in like_list: is_liked = 1
        else:                   is_liked = 0
        
        return {"is_user":1, "is_liked":is_liked, "is_marked":1}