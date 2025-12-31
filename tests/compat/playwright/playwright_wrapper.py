import sys
from importlib.util import find_spec, module_from_spec
from unittest import mock


class PlaywrightWrapper:
    """Ensures a 'playwright' import is available in sys.modules.

    - If 'playwright' isn't found, a MagicMock is registered so imports won't fail.
    - We then remove any existing 'playwright' from sys.modules to force a fresh
      import attempt from site-packages.
    - If the real import fails, we restore whatever was there originally and
      re-raise the error. (PlaywrightMock will be used as a fallback.)

    .. note::
        - The `submodules` list must be kept in sync with the real Playwright library
        to accurately mock any new or changed submodules.
        - If you encounter a `ModuleNotFoundError` for a missing submodule inside Playwright
        (e.g., `playwright._impl.some_new_submodule`), **add it here**.
    """

    def __init__(self) -> None:
        # Keep this list up to date as new submodules appear in real Playwright releases.
        # If you see a missing module error, add it here.
        module = "playwright"
        submodules = {
            "_impl": ["_errors"],  # Add more if needed
            "async_api": [],
            "driver": [],
            "sync_api": []
        }

        # If playwright isn't in sys.modules, register mocks so imports won't explode
        if module not in sys.modules:
            root_mock = mock.MagicMock()
            sys.modules[module] = root_mock

            for submodule, nested_submodules in submodules.items():
                mock_obj = mock.MagicMock()
                setattr(root_mock, submodule, mock_obj)
                sys.modules[f"{module}.{submodule}"] = mock_obj

                # Handle deep submodules like `playwright._impl._errors`
                for nested in nested_submodules:
                    nested_mock = mock.MagicMock()
                    setattr(mock_obj, nested, nested_mock)
                    sys.modules[f"{module}.{submodule}.{nested}"] = nested_mock

        # Temporarily remove playwright, forcing an actual site-packages import
        original_playwright = sys.modules.pop(module, None)

        try:
            # Attempt to import the real playwright from site-packages
            playwright_spec = find_spec("playwright")
            if not playwright_spec or not playwright_spec.origin:
                raise ModuleNotFoundError("No module named 'playwright'")
            if "site-packages" not in playwright_spec.origin and "dist-packages" not in playwright_spec.origin:
                raise ModuleNotFoundError("No module named 'playwright' in site-packages")
            real_module = module_from_spec(playwright_spec)
            playwright_spec.loader.exec_module(real_module)
        except ModuleNotFoundError as e:
            # If real import fails, restore what we had before and re-raise
            if original_playwright:
                sys.modules[module] = original_playwright
            raise e  # Fallback to PlaywrightMock next
