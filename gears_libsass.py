from gears.compilers import BaseCompiler

class SASSCompiler(BaseCompiler):
    result_mimetype = "text/css"

    def __call__(self, asset):
        asset.processed_source = "ha"
