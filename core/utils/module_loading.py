import importlib
import pkgutil
from pathlib import Path
from app.conf import settings


def auto_discover_models(package: str):
    """Імпортує всі модулі в `package`, щоб моделі реєструвалися автоматично"""

    full_package = package

    if package.startswith(settings.PROJECT_DIR.name):
        package = package[len(settings.PROJECT_DIR.name) + 1:] # If package starts with project name, remove it + 1 for the dot

    package_path = Path(settings.PROJECT_DIR, *package.split('.'))
    print(f"Discovering models from {package_path}")
    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        importlib.import_module(f"{full_package}.{module_name}")