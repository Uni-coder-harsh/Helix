import os

from helix_platform.config import DevConfig, get_settings


def test_get_settings_dev() -> None:
    """Verifies settings load development configurations correctly."""
    os.environ["HELIX_ENV"] = "dev"
    # Clear the caching to load a fresh config
    get_settings.cache_clear()
    settings = get_settings()

    assert settings.ENV == "dev"
    assert settings.LOG_LEVEL == "DEBUG"
    assert isinstance(settings, DevConfig)


def test_settings_properties() -> None:
    """Checks basic default properties of configurations."""
    settings = get_settings()
    assert settings.APP_NAME == "helix-backend"
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
