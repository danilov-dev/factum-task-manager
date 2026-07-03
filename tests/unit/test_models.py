# tests/unit/test_models.py
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.ideas.models import Idea
from tests.factories import IdeaFactory, IdeaRoleFactory, IdeaResponseFactory, UserFactory


@pytest.mark.django_db
class TestIdeaModel:
    def test_is_visible_property(self):
        """Тест видимости идеи"""
        # Видимая идея: опубликована и статус OPEN
        idea = IdeaFactory(
            is_published=True,
            status=Idea.Status.OPEN
        )
        assert idea.is_visible is True

        # Невидимая: не опубликована
        idea.is_published = False
        assert idea.is_visible is False

        # Невидимая: статус DRAFT
        idea.is_published = True
        idea.status = Idea.Status.DRAFT
        assert idea.is_visible is False

    def test_all_roles_filled_empty_roles(self):
        """Тест: если ролей нет, то all_roles_filled = False"""
        idea = IdeaFactory()
        assert idea.all_roles_filled is False

    def test_all_roles_filled_with_roles(self):
        """Тест заполнения всех ролей"""
        idea = IdeaFactory()
        role1 = IdeaRoleFactory(idea=idea, count_needed=2, count_filled=2)
        role2 = IdeaRoleFactory(idea=idea, count_needed=1, count_filled=0)

        # role2 не заполнена
        assert idea.all_roles_filled is False

        # Заполняем role2
        role2.count_filled = 1
        role2.save()

        assert idea.all_roles_filled is True

    def test_unfilled_roles_count(self):
        """Тест подсчета незаполненных ролей"""
        idea = IdeaFactory()
        IdeaRoleFactory(idea=idea, count_needed=2, count_filled=2)  # заполнена
        IdeaRoleFactory(idea=idea, count_needed=1, count_filled=0)  # не заполнена
        IdeaRoleFactory(idea=idea, count_needed=3, count_filled=1)  # не заполнена

        assert idea.unfilled_roles_count == 2


@pytest.mark.django_db
class TestIdeaRoleModel:
    def test_spots_left_calculation(self):
        """Тест подсчета оставшихся мест"""
        role = IdeaRoleFactory(count_needed=3, count_filled=1)
        assert role.spots_left == 2

        role.count_filled = 3
        assert role.spots_left == 0

        # Не может быть отрицательным
        role.count_filled = 5
        assert role.spots_left == 0

    def test_close_if_full(self):
        """Тест автоматического закрытия роли"""
        role = IdeaRoleFactory(count_needed=2, count_filled=1, is_open=True)

        role.count_filled = 2
        role.close_if_full()

        assert role.is_open is False


@pytest.mark.django_db
class TestIdeaResponseModel:
    def test_unique_constraint(self):
        """Тест уникальности отклика на роль"""
        user = UserFactory()
        role = IdeaRoleFactory()

        # Создаем первый отклик
        IdeaResponseFactory(user=user, role=role)

        # Пытаемся создать второй отклик на ту же роль
        with pytest.raises(IntegrityError):
            IdeaResponseFactory(user=user, role=role)

    def test_clean_method_role_closed(self):
        """Тест валидации: роль закрыта"""
        role = IdeaRoleFactory(is_open=False)
        response = IdeaResponseFactory.build(role=role)

        with pytest.raises(ValidationError):
            response.clean()

    def test_clean_method_no_spots(self):
        """Тест валидации: нет мест"""
        role = IdeaRoleFactory(count_needed=1, count_filled=1)
        response = IdeaResponseFactory.build(role=role)

        with pytest.raises(ValidationError):
            response.clean()

    def test_clean_method_author_cannot_respond(self):
        """Тест валидации: автор не может откликнуться"""
        author = UserFactory()
        idea = IdeaFactory(author=author)
        role = IdeaRoleFactory(idea=idea)
        response = IdeaResponseFactory.build(user=author, role=role, idea=idea)

        with pytest.raises(ValidationError):
            response.clean()