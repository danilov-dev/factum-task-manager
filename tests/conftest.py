import pytest
from django.test import Client
from tests.factories import UserFactory


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def another_user():
    return UserFactory()


@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    return client