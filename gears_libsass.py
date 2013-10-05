from gears.compilers import BaseCompiler
import os.path as path
import os
import re
import sass

class SASSCompiler(BaseCompiler):
    result_mimetype = "text/css"

    def __init__(self, *args, **kwargs):
        super(SASSCompiler, self).__init__(*args, **kwargs)
        self.parser = ImportParser()

    def __call__(self, asset):
        dependency_paths = self.parser.parse_imports(asset.absolute_path)
        asset.processed_source = sass.compile(
            string=str(asset.processed_source))
        for path in dependency_paths:
            asset.dependencies.add(path)


class ImportParser(object):

    def __init__(self):
        self.import_re = re.compile(r"""@import\s+["']?([^;"']*);?""")
        self.parsed_files = set()

    def parse_imports(self, filename):
        raw = open(filename).read()
        matches = self.import_re.findall(raw)
        dependencies = set([self._get_path(filename, match) for match in matches])
        result = set([filename])
        for dep in dependencies:
            if dep not in self.parsed_files:
                self.parsed_files.add(dep)
                result = result.union(self.parse_imports(dep))
        self.parsed_files = set()
        result = dependencies.union(result)
        result.remove(filename)
        return result

    def _get_path(self, current_file, match_result):
        file_dir = path.dirname(current_file)
        import_path = path.abspath(file_dir + "/" + match_result) + ".scss"
        partial_path = self._create_partial_filename(import_path)
        if path.isfile(partial_path):
            import_path = partial_path
        return import_path

    def _create_partial_filename(self, abs_filename):
        partial_dir = path.dirname(abs_filename)
        partial_file = "_" + path.basename(abs_filename)
        return path.join(partial_dir, partial_file)


