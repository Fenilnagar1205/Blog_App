from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView, Response
from .serializers import CommentSerializer
from .permissions import IsCommentOwnerOrAdmin
from blogs.models import Blog
from .models import Comment, Like

# Create your views here.


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        blog_id = self.kwargs["blog_id"]
        blog = get_object_or_404(Blog, id=blog_id, status=Blog.Status.PUBLISHED)
        serializer.save(author=self.request.user, blog=blog)

    def get_queryset(self):
        blog_id = self.kwargs["blog_id"]
        return Comment.objects.filter(
            blog__id=blog_id, blog__status=Blog.Status.PUBLISHED
        )


class CommentDeleteView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsCommentOwnerOrAdmin]

    def get_queryset(self):
        return Comment.objects.filter(blog__status="PB")


class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, blog_id):
        blog = get_object_or_404(Blog, id=blog_id, status=Blog.Status.PUBLISHED)
        already_liked = Like.objects.filter(user=request.user, blog=blog).exists()

        if already_liked:
            Like.objects.filter(user=request.user, blog=blog).delete()
            return Response(
                {"message": "Like Removed"},
                status=status.HTTP_200_OK,
            )
        else:
            Like.objects.create(blog=blog, user=self.request.user)
            return Response(
                {"message": "Blog Liked"},
                status=status.HTTP_201_CREATED,
            )
