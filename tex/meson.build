
tex_install_dir = get_option('datadir') / meson.project_name() / 'tex'

# This one is not part of the class and is always installed for the report
install_data(
    'sdapsreport.cls',
    install_tag: 'tex',
    install_dir: tex_install_dir,
)

texlua = find_program('texlua')

# The files build.lua will create, needs to be updated for the file to install
tex_files = [
    'sdapsarray.sty',
    'sdapsbase.sty',
    'sdapsclassic.cls',
    'sdapslayout.sty',
    'sdapspdf.sty',
    'sdapscode128.tex',
]

tex_in = []
tex_out = []
foreach tex_file: tex_files
    tex_in += 'class' / tex_file.replace('.sty', '.dtx').replace('.cls', '.dtx')
    tex_out += tex_file
endforeach

sdaps_tex = custom_target('tex-class',
    input: tex_in,
    output: tex_out,
    command: [ texlua, meson.current_source_dir() / 'build.lua', 'unpack' ],
    env: {
        'SOURCE': meson.current_source_dir(),
        'BUILD': meson.current_build_dir(),
    },
    install: get_option('latex'),
    install_tag: 'tex',
    install_dir: tex_install_dir
)

if get_option('test-latex')
    test('latex-class',
         texlua, args: [ meson.current_source_dir() / 'build.lua', 'check' ],
         timeout: 60,
         env: {
             'SOURCE': meson.current_source_dir(),
             'BUILD': meson.current_build_dir(),
         },
    )
else
    # Make it explicit that we do not run this
    test('latex-class', find_program('sh'), args: ['-c', 'exit 77'])
endif
