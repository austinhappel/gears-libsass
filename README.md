A gears compiler which uses libsass to compile input. It also recursively scans input files to add dependencies so for example, if your scss file has this line

    @import 'some_file';

Then `some_file` will be added as  gears dependency, thus triggering recompiles if it changes.
