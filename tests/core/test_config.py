import pytest
from app.core.config import get_settings, Settings

def test_get_settings():
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert hasattr(settings, 'ENV')
    assert hasattr(settings, 'tasURL')
    assert hasattr(settings, 'tasUser')
    assert hasattr(settings, 'tasSecret')
    assert hasattr(settings, 'jwtSecret')
    assert hasattr(settings, 'alg')

def test_settings_singleton():
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2

@pytest.mark.parametrize("env", ["dev", "prod", "test"])
def test_settings_environment(env, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", env)
    settings = get_settings()
    assert settings.ENV == env

def test_settings_required_values():
    settings = get_settings()
    assert settings.tasURL is not None
    assert settings.tasUser is not None
    assert settings.tasSecret is not None
    assert settings.jwtSecret is not None
    assert settings.alg is not None
    assert settings.POSTGRES_PASSWORD is not None
    assert settings.DATABASE_URL is not None

def test_settings_jwt_config():
    settings = get_settings()
    assert isinstance(settings.jwtSecret, str)
    assert len(settings.jwtSecret) > 0
    assert settings.alg in ["HS256", "HS384", "HS512"]  # Common JWT algorithms