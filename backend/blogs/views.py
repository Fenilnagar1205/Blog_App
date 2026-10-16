from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from rest_framework import generics, permissions, status
from rest_framework.views import APIView, Response
from rest_framework.generics import get_object_or_404
from rest_framework.filters import SearchFilter

from .serializers import BlogSerializer
from .models import Blog
from .permissions import IsOwnerOrAdmin

# Create your views here.


class BlogListCreateView(generics.ListCreateAPIView):
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["title", "content"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Blog.objects.all()

        return Blog.objects.filter(Q(status=Blog.Status.PUBLISHED) | Q(author=user))

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        author_id = self.request.query_params.get("author")

        if author_id:
            queryset = queryset.filter(author_id=author_id)

        return queryset


class BlogDetailView(generics.RetrieveAPIView):
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return Blog.objects.filter(Q(status=Blog.Status.PUBLISHED) | Q(author=user))


class BlogUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = BlogSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Blog.objects.all()

        return Blog.objects.filter(Q(status=Blog.Status.PUBLISHED) | Q(author=user))


class PublishBlogView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def post(self, request, pk):
        # Yahan publishing logic aayega
        user = self.request.user

        if user.is_staff:
            user_blogs_qs = Blog.objects.all()
        else:
            user_blogs_qs = Blog.objects.filter(
                Q(status=Blog.Status.PUBLISHED) | Q(author=user)
            )

        blog = get_object_or_404(user_blogs_qs, pk=pk)
        # print("REQUEST USER:", request.user.id)
        # print("BLOG AUTHOR:", blog.author_id)
        # print("IS STAFF:", request.user.is_staff)

        self.check_object_permissions(request, blog)
        if blog.status == Blog.Status.DRAFT:

            blog.status = Blog.Status.PUBLISHED
            blog.published_at = timezone.now()
        else:
            return Response(
                {"message": "Blog is already published."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        blog.save()
        serializer = BlogSerializer(blog)
        return Response(serializer.data)
