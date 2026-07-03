import pytest
from django.core.exceptions import ValidationError
from apps.ideas.models import Idea, IdeaResponse
from apps.ideas.services.idea import create_idea, update_idea, get_visible_ideas
from apps.ideas.services.response import create_response, approve_response, reject_response
from tests.factories import IdeaFactory, IdeaRoleFactory, IdeaResponseFactory, UserFactory


@pytest.mark.django_db
class TestIdeaServices:
    def test_create_idea(self):
        """Тест создания идеи"""
        user = UserFactory()

        idea = create_idea(
            author=user,
            title='Test Idea',
            about='About',
            description='Description',
            category=Idea.Category.IT
        )

        assert idea.title == 'Test Idea'
        assert idea.author == user
        assert idea.status == Idea.Status.DRAFT
        assert idea.is_published is False

    def test_update_idea(self):
        """Тест обновления идеи"""
        idea = IdeaFactory()

        update_idea(
            idea_id=idea.id,
            title='Updated Title',
            about='Updated About',
            description='Updated Description',
            category=Idea.Category.ECOLOGY,
            status=Idea.Status.OPEN
        )

        idea.refresh_from_db()
        assert idea.title == 'Updated Title'
        assert idea.status == Idea.Status.OPEN
        assert idea.category == Idea.Category.ECOLOGY

    def test_get_visible_ideas(self):
        """Тест получения видимых идей"""
        IdeaFactory(is_published=True, status=Idea.Status.OPEN)
        IdeaFactory(is_published=True, status=Idea.Status.TEAM_ASSEMBLED)
        IdeaFactory(is_published=True, status=Idea.Status.DRAFT)
        IdeaFactory(is_published=False, status=Idea.Status.OPEN)

        visible = get_visible_ideas()
        assert visible.count() == 2


@pytest.mark.django_db
class TestResponseServices:
    def test_create_response_success(self):
        """Тест успешного создания отклика"""
        user = UserFactory()
        role = IdeaRoleFactory(count_needed=2, count_filled=0)

        response = create_response(
            user=user,
            role_id=role.id,
            message='I want to join'
        )

        assert response.user == user
        assert response.role == role
        assert response.status == IdeaResponse.Status.PENDING

    def test_create_response_author_cannot_respond(self):
        """Тест: автор не может откликнуться на свою идею"""
        author = UserFactory()
        idea = IdeaFactory(author=author)
        role = IdeaRoleFactory(idea=idea)

        with pytest.raises(ValidationError) as exc_info:
            create_response(user=author, role_id=role.id, message='Test')

        assert 'не можете откликнуться на свою идею' in str(exc_info.value)

    def test_create_response_role_closed(self):
        """Тест отклика на закрытую роль"""
        user = UserFactory()
        role = IdeaRoleFactory(is_open=False)

        with pytest.raises(ValidationError) as exc_info:
            create_response(user=user, role_id=role.id, message='Test')

        assert 'Набор на эту роль закрыт' in str(exc_info.value)

    def test_create_response_no_spots(self):
        """Тест отклика когда нет мест"""
        user = UserFactory()
        role = IdeaRoleFactory(count_needed=1, count_filled=1)

        with pytest.raises(ValidationError) as exc_info:
            create_response(user=user, role_id=role.id, message='Test')

        assert 'места на эту роль уже заняты' in str(exc_info.value)

    def test_create_response_duplicate(self):
        """Тест повторного отклика"""
        user = UserFactory()
        role = IdeaRoleFactory()

        create_response(user=user, role_id=role.id, message='First')

        with pytest.raises(ValidationError) as exc_info:
            create_response(user=user, role_id=role.id, message='Second')

        assert 'уже откликались' in str(exc_info.value)

    def test_approve_response(self):
        """Тест одобрения отклика"""
        author = UserFactory()
        idea = IdeaFactory(author=author)
        role = IdeaRoleFactory(idea=idea, count_needed=2, count_filled=0)
        response = IdeaResponseFactory(role=role, idea=idea, status=IdeaResponse.Status.PENDING)

        approved = approve_response(response_id=response.id, author=author)

        assert approved.status == IdeaResponse.Status.APPROVED

        role.refresh_from_db()
        assert role.count_filled == 1

    def test_approve_response_not_author(self):
        """Тест: только автор может одобрять"""
        author = UserFactory()
        another_user = UserFactory()
        idea = IdeaFactory(author=author)
        role = IdeaRoleFactory(idea=idea)
        response = IdeaResponseFactory(role=role, idea=idea)

        with pytest.raises(ValidationError) as exc_info:
            approve_response(response_id=response.id, author=another_user)

        assert 'Только автор идеи' in str(exc_info.value)

    def test_approve_response_no_spots(self):
        """Тест одобрения когда нет мест"""
        author = UserFactory()
        idea = IdeaFactory(author=author)
        role = IdeaRoleFactory(idea=idea, count_needed=1, count_filled=1)
        response = IdeaResponseFactory(role=role, idea=idea)

        with pytest.raises(ValidationError) as exc_info:
            approve_response(response_id=response.id, author=author)

        assert 'Нет свободных мест' in str(exc_info.value)

    def test_approve_response_closes_role_when_full(self):
        """Тест: роль закрывается при заполнении"""
        author = UserFactory()
        idea = IdeaFactory(author=author)
        role = IdeaRoleFactory(idea=idea, count_needed=1, count_filled=0, is_open=True)
        response = IdeaResponseFactory(role=role, idea=idea)

        approve_response(response_id=response.id, author=author)

        role.refresh_from_db()
        assert role.is_open is False
        assert role.count_filled == 1

    def test_reject_response(self):
        """Тест отклонения отклика"""
        author = UserFactory()
        idea = IdeaFactory(author=author)
        role = IdeaRoleFactory(idea=idea)
        response = IdeaResponseFactory(role=role, idea=idea, status=IdeaResponse.Status.PENDING)

        rejected = reject_response(response_id=response.id, author=author)

        assert rejected.status == IdeaResponse.Status.REJECTED

    def test_reject_response_not_author(self):
        """Тест: только автор может отклонять"""
        author = UserFactory()
        another_user = UserFactory()
        idea = IdeaFactory(author=author)
        role = IdeaRoleFactory(idea=idea)
        response = IdeaResponseFactory(role=role, idea=idea)

        with pytest.raises(ValidationError):
            reject_response(response_id=response.id, author=another_user)