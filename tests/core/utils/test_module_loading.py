from pathlib import Path
from unittest.mock import patch, MagicMock
from core.config import settings
from core.utils.module_loading import auto_discover_models


def test_auto_discover_models():
    package = "core.models"
    package_path = Path(settings.APP_DIR, *package.split("."))
    mock_iter_modules = [(None, "test_model", None)]

    with patch("pkgutil.iter_modules", return_value=mock_iter_modules) as mock_pkgutil:
        with patch("importlib.import_module") as mock_import_module:
            auto_discover_models(package)
            mock_pkgutil.assert_called_once_with([str(package_path)])
            mock_import_module.assert_called_once_with("core.models.test_model")
