from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from blogs.models import Blog
from interactions.models import Comment, Like


class InteractionsAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="interactionuser",
            email="interaction@example.com",
            password="StrongPass123!xyz",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="StrongPass123!xyz",
        )
        self.admin = User.objects.create_superuser(
            username="interactionadmin",
            email="admin@example.com",
            password="StrongPass123!xyz",
        )

        self.blog = Blog.objects.create(
            title="Published Blog",
            content="Published content",
            author=self.user,
            status=Blog.Status.PUBLISHED,
            slug="published-interaction-blog",
        )
        self.draft = Blog.objects.create(
            title="Draft Blog",
            content="Draft content",
            author=self.user,
            status=Blog.Status.DRAFT,
            slug="draft-interaction-blog",
        )

        self.client.force_authenticate(user=self.user)

    def test_user_can_create_comment_on_published_blog(self):
        response = self.client.post(
            f"/blogs/{self.blog.id}/comments/",
            {"content": "Great blog!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Comment.objects.filter(
                blog=self.blog, author=self.user, content="Great blog!"
            ).exists()
        )

    def test_user_cannot_comment_on_draft_blog(self):
        response = self.client.post(
            f"/blogs/{self.draft.id}/comments/",
            {"content": "Comment on draft"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_delete_own_comment(self):
        comment = Comment.objects.create(
            blog=self.blog,
            author=self.user,
            content="My comment",
        )

        response = self.client.delete(f"/blogs/comments/{comment.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_other_user_cannot_delete_comment(self):
        comment = Comment.objects.create(
            blog=self.blog,
            author=self.user,
            content="Owner comment",
        )
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(f"/blogs/comments/{comment.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_comment(self):
        comment = Comment.objects.create(
            blog=self.blog,
            author=self.user,
            content="Comment for admin test",
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(f"/blogs/comments/{comment.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_can_like_published_blog(self):
        response = self.client.post(f"/blogs/{self.blog.id}/like/")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Like.objects.filter(blog=self.blog, user=self.user).exists())

    def test_second_like_request_removes_like(self):
        self.client.post(f"/blogs/{self.blog.id}/like/")
        response = self.client.post(f"/blogs/{self.blog.id}/like/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Like.objects.filter(blog=self.blog, user=self.user).exists())

    def test_user_cannot_like_draft_blog(self):
        response = self.client.post(f"/blogs/{self.draft.id}/like/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(Like.objects.filter(blog=self.draft, user=self.user).exists())

    def test_like_model_prevents_duplicate_likes(self):
        Like.objects.create(blog=self.blog, user=self.user)

        with self.assertRaises(Exception):
            Like.objects.create(blog=self.blog, user=self.user)
