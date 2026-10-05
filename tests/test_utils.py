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
