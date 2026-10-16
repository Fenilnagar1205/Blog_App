from django.urls import path
from .views import BlogListCreateView, BlogUpdateDeleteView, PublishBlogView

urlpatterns = [
    path("", BlogListCreateView.as_view(), name="blog-list"),
    path("<int:pk>/", BlogUpdateDeleteView.as_view(), name="blog-update-delete"),
    path("<int:pk>/publish/", PublishBlogView.as_view(), name="blog-publish"),
]
