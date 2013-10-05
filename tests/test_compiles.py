from gears.environment import Environment
from gears.finders import FileSystemFinder
from gears_libsass import SASSCompiler
from os import path
import os
import unittest

fixtures_dir = path.abspath(path.join(path.dirname(__file__), "fixtures"))

def load_fixture(filename):
    fixture_path = path.join(fixtures_dir, filename)
    return open(fixture_path).read()

class SassCompilerTestCase(unittest.TestCase):

    def setUp(self):
        self.expected_output_file = path.join(path.dirname(__file__), "main.css.scss")
        if path.isfile(self.expected_output_file):
            os.remove(self.expected_output_file)

    def test_compiles_correctly(self):
        environment = Environment(
            root=fixtures_dir,
            public_assets=(r".*\.scss",),
            fingerprinting=False,
        )
        compiler = SASSCompiler()
        environment.compilers.register(".scss", compiler)
        environment.finders.register(FileSystemFinder(directories=(fixtures_dir,)))
        environment.save()
        expected_content = load_fixture("expected_content.css")
        actual_content = load_fixture("main.css")
        self.assertEqual(expected_content, actual_content)
