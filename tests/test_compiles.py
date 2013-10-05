from gears.environment import Environment
from gears.finders import FileSystemFinder
from gears_libsass import SASSCompiler, ImportParser
import glob
from os import path
import os
import unittest
import shutil

fixtures_dir = path.abspath(path.join(path.dirname(__file__), "fixtures"))

def load_fixture(filename):
    fixture_path = path.join(fixtures_dir, filename)
    return open(fixture_path).read()

class AbstractSassCompilerTestCase(unittest.TestCase):

    def setUp(self):
        self.output_files = []
        self.addCleanup(self.remove_output_files)

    def remove_output_files(self):
        output_glob = path.join(fixtures_dir, "output", "*")
        for output_file in glob.glob(output_glob):
            if path.isdir(output_file):
                shutil.rmtree(output_file)
            else:
                os.remove(output_file)

    def setup_environment(self, directory):
        os.chdir(directory)
        self.environment = Environment(
            root=path.join(fixtures_dir, "output"),
            public_assets=(r".*\.css",),
            fingerprinting=False,
        )
        self.compiler = SASSCompiler()
        self.environment.compilers.register(".scss", self.compiler)
        self.environment.finders.register(FileSystemFinder(directories=(directory,)))
        self.environment.register_defaults()


class SassCompilerTestCase(AbstractSassCompilerTestCase):

    def test_compiles_correctly(self):
        self.setup_environment(path.join(fixtures_dir, "single_file_test"))
        self.environment.save()
        expected_content = load_fixture("single_file_test/expected_content.css")
        expected_output_file = path.join(fixtures_dir, "output/main.css")
        self.output_files.append(expected_output_file)
        actual_content = load_fixture(expected_output_file)
        self.assertEqual(expected_content, actual_content)

    def test_dependencies_loaded(self):
        self.setup_environment(path.join(fixtures_dir, "single_dependency_test"))
        self.environment.save()
        expected_content = load_fixture("single_dependency_test/expected_content.css")
        expected_output_file = path.join(fixtures_dir, "output/main.css")
        self.output_files.append(expected_output_file)
        actual_content = load_fixture(expected_output_file)
        self.assertEqual(expected_content, actual_content)

    def test_dependencies_loaded_in_child_subdir(self):
        self.setup_environment(path.join(fixtures_dir, "wrong_directory_tests"))
        self.environment.save()
        expected_content = load_fixture("wrong_directory_tests/expected_content.css")
        expected_output_file = path.join(fixtures_dir, "output/subdir/main.css")
        self.output_files.append(expected_output_file)
        actual_content = load_fixture(expected_output_file)
        self.assertEqual(expected_content, actual_content)

class DependencyChangeTestCase(AbstractSassCompilerTestCase):

    def change_file_contents(self, filename, new_contents):
        backup_file = path.join(path.dirname(filename), ".backup")
        shutil.copyfile(filename, backup_file)
        with open(filename, "w") as outfile:
            outfile.write(new_contents)
        self.addCleanup(lambda: self.restore_file(filename))

    def restore_file(self, filename):
        backup_file = path.join(path.dirname(filename), ".backup")
        shutil.copyfile(backup_file, filename)
        os.remove(backup_file)

    def test_reloads_on_dependency_change(self):
        test_dir = path.join(fixtures_dir, "single_dependency_changing_test")
        self.setup_environment(path.join(fixtures_dir, test_dir))
        self.environment.save()
        self.change_file_contents(path.join(test_dir, "_dependency.scss"),
                                 "@mixin halfwidth{\n"
                                 "     width:25%;\n"
                                 "}")
        self.environment.save()
        expected_content = load_fixture("single_dependency_changing_test/expected_content.css")
        expected_output_file = path.join(fixtures_dir, "output/main.css")
        self.output_files.append(expected_output_file)
        actual_content = load_fixture(expected_output_file)
        self.assertEqual(expected_content, actual_content)


    def test_reloads_on_transitive_dependency_change(self):
        test_dir = path.join(fixtures_dir, "transitive_dependency_changing_test")
        self.setup_environment(path.join(fixtures_dir, test_dir))
        self.environment.save()
        self.change_file_contents(path.join(test_dir, "_transitive_dependency.scss"),
                                  "$constantwidth:25%;")
        self.environment.save()
        expected_content = load_fixture("transitive_dependency_changing_test/expected_content.css")
        expected_output_file = path.join(fixtures_dir, "output/main.css")
        self.output_files.append(expected_output_file)
        actual_content = load_fixture(expected_output_file)
        self.assertEqual(expected_content, actual_content)


class ImportParserTestCase(unittest.TestCase):

    def setUp(self):
        self.import_dir = path.join(fixtures_dir, "import_parsing_tests")

    def test_parses_imports_correctly(self):
        parser = ImportParser()
        imports = parser.parse_imports(path.join(self.import_dir, "simple_import.scss"))
        expected_imports = [
            path.join(self.import_dir, "thingy.scss"),
            path.join(self.import_dir, "_otherthingy.scss"),
        ]
        self.assertEqual(list(imports), expected_imports)

    def test_parses_transitive_imports_correctly(self):
        parser = ImportParser()
        imports = parser.parse_imports(path.join(self.import_dir, "transitive_import.scss"))
        expected_imports = [
            path.join(self.import_dir, "_transitive_dependency.scss"),
            path.join(self.import_dir, "thingy.scss"),
        ]
        self.assertEqual(list(imports), expected_imports)

    def test_parses_circular_imports_correctly(self):
        parser = ImportParser()
        imports = parser.parse_imports(path.join(self.import_dir, "circular_import_one.scss"))
        expected_imports = [
            path.join(self.import_dir, "circular_import_two.scss"),
        ]
        self.assertEqual(list(imports), expected_imports)
