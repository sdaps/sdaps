
# strict vs. non-strict mode
environ = {
    'BUILDDIR' : meson.project_build_root(),
    'IGNORE_PATTERN_EXTEND' : get_option('test-latex') ? '' : '\|^survey_id',
}

test('test-run',
     find_program('run-test-locally.sh'),
     timeout: 240,
     env: environ,
     depends: [sdaps_ext, sdaps_tex],
     workdir: meson.current_build_dir())
