from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from blogs.models import Blog


class BlogAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="blogowner",
            email="owner@example.com",
            password="StrongPass123!xyz",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="StrongPass123!xyz",
        )
        self.admin = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="StrongPass123!xyz",
        )

        self.blog = Blog.objects.create(
            title="Published Blog",
            content="Published content",
            author=self.user,
            status=Blog.Status.PUBLISHED,
            slug="published-blog",
        )
        self.draft = Blog.objects.create(
            title="Draft Blog",
            content="Draft content",
            author=self.user,
            status=Blog.Status.DRAFT,
            slug="draft-blog",
        )

        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_create_blog(self):
        response = self.client.post(
            "/blogs/",
            {
                "title": "New Blog",
                "content": "New content",
                "slug": "new-blog",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], self.user.id)
        self.assertEqual(response.data["status"], Blog.Status.DRAFT)

    def test_anonymous_user_cannot_create_blog(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            "/blogs/",
            {
                "title": "Anonymous Blog",
                "content": "Content",
                "slug": "anonymous-blog",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_see_own_draft(self):
        response = self.client.get("/blogs/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        blog_ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.draft.id, blog_ids)

    def test_user_cannot_see_another_users_draft(self):
        other_draft = Blog.objects.create(
            title="Other Draft",
            content="Private draft",
            author=self.other_user,
            status=Blog.Status.DRAFT,
            slug="other-draft",
        )

        response = self.client.get("/blogs/")
        blog_ids = [item["id"] for item in response.data["results"]]

        self.assertNotIn(other_draft.id, blog_ids)

    def test_other_user_cannot_update_blog(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            f"/blogs/{self.blog.id}/",
            {"title": "Changed title"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_update_own_blog(self):
        response = self.client.patch(
            f"/blogs/{self.draft.id}/",
            {"title": "Updated Draft"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.title, "Updated Draft")

    def test_owner_can_publish_draft(self):
        response = self.client.post(f"/blogs/{self.draft.id}/publish/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.status, Blog.Status.PUBLISHED)
        self.assertIsNotNone(self.draft.published_at)

    def test_publishing_already_published_blog_returns_400(self):
        response = self.client.post(f"/blogs/{self.blog.id}/publish/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_update_another_users_blog(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f"/blogs/{self.draft.id}/",
            {"title": "Admin Updated Draft"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_delete_own_blog(self):
        response = self.client.delete(f"/blogs/{self.draft.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Blog.objects.filter(id=self.draft.id).exists())
