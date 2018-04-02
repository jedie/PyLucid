import sys
from pathlib import Path


class Requirements:
    DEVELOPER_INSTALL="developer"
    NORMAL_INSTALL="normal"
    REQUIREMENTS = {
        DEVELOPER_INSTALL: "developer_installation.txt",
        NORMAL_INSTALL: "normal_installation.txt",
    }
    def __init__(self, package_path):
        assert package_path.is_dir()
        self.package_path = package_path

        self.src_path = Path(sys.prefix, "src")
        src_pylucid_path = Path(self.src_path, "pylucid")
        if src_pylucid_path.is_dir():
            print("PyLucid is installed as editable here: %s" % src_pylucid_path)
            self.install_mode=self.DEVELOPER_INSTALL
        else:
            print("PyLucid is installed as packages here: %s" % self.package_path)
            self.install_mode=self.NORMAL_INSTALL

    @property
    def normal_mode(self):
        return self.install_mode == self.NORMAL_INSTALL

    def get_requirement_path(self):
        """
        :return: Path(.../pylucid/requirements/)
        """
        requirement_path = Path(self.package_path, "requirements").resolve()
        if not requirement_path.is_dir():
            raise RuntimeError("Requirements directory not found here: %s" % requirement_path)
        return requirement_path

    def get_requirement_file_path(self):
        """
        :return: Path(.../pylucid/requirements/<mode>_installation.txt)
        """
        requirement_path = self.get_requirement_path()
        filename = self.REQUIREMENTS[self.install_mode]

        requirement_file_path = Path(requirement_path, filename).resolve()
        if not requirement_file_path.is_file():
            raise RuntimeError("Requirements file not found here: %s" % requirement_file_path)

        return requirement_file_path


if __name__ == '__main__':
    import pylucid
    package_path = Path(pylucid.__file__).parent
    req = Requirements(package_path=package_path)
    print("requirement_path.......:", req.get_requirement_path())
    print("requirement_file_path..:", req.get_requirement_file_path())
