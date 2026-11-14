import logging

from apikeyper.log_engine import Loggable, MOD_LOGGER, ROOT_LOGGER
from apikeyper.utils import PackageChecker


class TestPackageChecker:
    def test_installed_package_detected(self):
        checker = PackageChecker(["pytest"])

        assert checker.check_installed_packages() == {"pytest": True}

    def test_missing_package_detected(self):
        checker = PackageChecker(["definitely-not-a-real-package-xyz"])

        assert checker.check_installed_packages() == {
            "definitely-not-a-real-package-xyz": False
        }

    def test_mixed_packages(self):
        checker = PackageChecker(["pytest", "definitely-not-a-real-package-xyz"])

        assert checker.check_installed_packages() == {
            "pytest": True,
            "definitely-not-a-real-package-xyz": False,
        }


def test_package_logging_inherits_console_only_settings():
    checker = PackageChecker([])

    assert isinstance(checker, Loggable)
    assert ROOT_LOGGER.get_child("log_engine") is MOD_LOGGER
    assert checker.log_device is ROOT_LOGGER.get_child("utils.PackageChecker")
    for logger in (ROOT_LOGGER, MOD_LOGGER, checker.log_device):
        assert logger.console_level == logging.INFO
        assert logger.no_file_logging
