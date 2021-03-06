from time import sleep
import logging
from importlib import import_module

log = logging.getLogger(__name__)


def first(items, name_plural='items'):
    assert items, f"No {name_plural} found"

    if len(items) > 1:
        log.warning(
            f"Found multiple {name_plural}: %r, choosing the first one",
            items,
        )

    return items[0]


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    # Borrowed from `django.utils.module_loading.import_string`
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        msg = f"{dotted_path} doesn't look like a module path"
        raise ImportError(msg) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        msg = f"Module {module_path!r} does not define {class_name!r}"
        raise ImportError(msg) from err


def retry(count=4, wait_sec=5, exp=2):
    def _retry(f):
        def wrapper(*args, **kwargs):
            current_wait = wait_sec
            for i in range(count):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    log.exception(e)
                    if i == count - 1:
                        raise

                    log.warning("#%s/%s retrying in %s sec", i + 1, count, current_wait)
                    current_wait = int(current_wait * exp)
                    sleep(current_wait)
                    continue
        return wrapper

    return _retry
