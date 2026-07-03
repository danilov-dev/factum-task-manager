import factory
from django.contrib.auth import get_user_model
from apps.ideas.models import Idea, IdeaRole, IdeaResponse

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True


class IdeaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Idea

    author = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f'Idea {n}')
    about = factory.Faker('text', max_nb_chars=200)
    description = factory.Faker('text')
    category = Idea.Category.IT
    status = Idea.Status.OPEN
    is_published = True


class IdeaRoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IdeaRole

    idea = factory.SubFactory(IdeaFactory)
    title = factory.Sequence(lambda n: f'Role {n}')
    description = factory.Faker('text')
    count_needed = 3
    count_filled = 0
    is_open = True


class IdeaResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IdeaResponse

    idea = factory.SubFactory(IdeaFactory)
    user = factory.SubFactory(UserFactory)
    role = factory.SubFactory(IdeaRoleFactory)
    message = factory.Faker('text')
    status = IdeaResponse.Status.PENDING