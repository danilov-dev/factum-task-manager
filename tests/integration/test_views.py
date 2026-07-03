import pytest
from django.urls import reverse

from apps.ideas.models import Idea
from tests.factories import IdeaFactory, IdeaRoleFactory, IdeaResponseFactory, UserFactory


@pytest.mark.django_db
class TestIdeaViews:
    def test_idea_list_view(self, client):
        """Тест списка идей"""
        IdeaFactory.create_batch(5, status='open')

        response = client.get(reverse('ideas:idea_list'))

        assert response.status_code == 200
        assert len(response.context['ideas']) == 5

    def test_idea_detail_view(self, client):
        """Тест детальной страницы идеи"""
        idea = IdeaFactory(status='published')

        response = client.get(reverse('ideas:detail', kwargs={'pk': idea.pk}))

        assert response.status_code == 200
        assert response.context['idea'] == idea

    def test_create_idea_view_authenticated(self, authenticated_client, user):
        """Тест создания идеи авторизованным пользователем"""
        data = {
            'title': 'New Idea',
            'about': 'About',
            'description': 'Description',
            'category': 1,
            'status': 'open'
        }

        response = authenticated_client.post(reverse('ideas:create'), data)

        assert response.status_code == 302  # redirect
        assert Idea.objects.filter(title='New Idea').exists()

    def test_create_idea_view_unauthenticated(self, client):
        """Тест создания идеи неавторизованным пользователем"""
        response = client.get(reverse('ideas:create'))

        assert response.status_code == 302

    def test_edit_idea_view_author(self, authenticated_client, user):
        """Тест редактирования идеи автором"""
        idea = IdeaFactory(author=user)

        response = authenticated_client.get(
            reverse('ideas:edit', kwargs={'pk': idea.pk})
        )

        assert response.status_code == 200

    def test_edit_idea_view_not_author(self, authenticated_client, user):
        """Тест редактирования идеи не автором"""
        another_user = UserFactory()
        idea = IdeaFactory(author=another_user)

        response = authenticated_client.get(
            reverse('ideas:edit', kwargs={'pk': idea.pk})
        )

        assert response.status_code == 302


@pytest.mark.django_db
class TestResponseViews:
    def test_approve_response_view(self, authenticated_client, user):
        """Тест одобрения отклика"""
        idea = IdeaFactory(author=user)
        role = IdeaRoleFactory(idea=idea)
        response = IdeaResponseFactory(role=role, status='pending')

        result = authenticated_client.post(
            reverse('ideas:approve_response', kwargs={'response_id': response.pk})
        )

        assert result.status_code == 302
        response.refresh_from_db()
        assert response.status == 'approved'

    def test_approve_response_view_not_author(self, authenticated_client, user):
        """Тест одобрения отклика не автором идеи"""
        another_user = UserFactory()
        idea = IdeaFactory(author=another_user)
        role = IdeaRoleFactory(idea=idea)
        response = IdeaResponseFactory(role=role, status='pending')

        result = authenticated_client.post(
            reverse('ideas:approve_response', kwargs={'response_id': response.pk})
        )

        assert result.status_code == 302