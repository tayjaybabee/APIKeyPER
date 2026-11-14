from apikeyper.log_engine import Logger
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


def test_find_child_by_name():
    parent = Logger("test_find_child_by_name")
    first = parent.get_child("first")
    second = parent.get_child("second")
    first_name, second_name = parent.get_child_names()

    assert parent.find_child_by_name(first_name) is first
    assert parent.find_child_by_name(second_name) is second
    assert parent.find_child_by_name("second") is None
    assert parent.find_child_by_name("unknown") is None
