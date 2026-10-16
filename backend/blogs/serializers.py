from rest_framework import serializers
from .models import Blog
from interactions.models import Like, Comment


class BlogSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = "__all__"
        read_only_fields = ["author", "status"]

    def get_like_count(self, obj):
        count = Like.objects.filter(blog=obj).count()

        return count

    def get_is_liked(self, obj):
        # user = self.context["request"].user
        # return Like.objects.filter(blog=obj, user=user).exists()
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return Like.objects.filter(blog=obj, user=request.user).exists()

    def get_comment_count(self, obj):
        count = Comment.objects.filter(blog=obj).count()

        return count
