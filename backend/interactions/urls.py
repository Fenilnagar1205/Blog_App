from django.urls import path
from .views import CommentDeleteView, CommentListCreateView, LikeView

urlpatterns = [
    path("<int:blog_id>/comments/", CommentListCreateView.as_view()),
    path("comments/<int:pk>/", CommentDeleteView.as_view(), name="comment-delete"),
    path("<int:blog_id>/like/", LikeView.as_view(), name="blog-like"),
]
