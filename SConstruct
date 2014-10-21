import os
from subprocess import check_output
from collections import OrderedDict
import re

import jinja2
from path_helpers import path


def build_wxi(target, source, env):
    '''
    Build WiX header file, defining the application details for the current
    installer build.

    The header includes details such as the MicroDrop application version
    number, which is also used as the version number for the installer.
    '''
    # Use `pkg_resources` to determine the version of the MicroDrop Python
    # package that was installed in the portable-Python environment to be
    # included in the installer.  The version of the MicroDrop package is also
    # used as the version number for the installer.
    version_text = check_output('%s -c "import pkg_resources; print '
                                'pkg_resources.get_distribution'
                                '(\'microdrop\')"' % microdrop_python)
    # Parse the version number components from the MicroDrop version string
    # returned from `pkg_resources`.  These version components are used to
    # populate the corresponding version tags in the WiX header template.
    version_match = re.search(r'microdrop (?P<major>\d+)\.(?P<minor>\d+)'
                              '\.post(?P<post>\d+)\.dev(?P<dev>\d+)',
                              version_text)
    version_tags = OrderedDict([(k, version_match.group(k))
                                for k in ('major', 'minor', 'post', 'dev')])

    wxi_template = jinja2.Template(path('Includes/AppVariables.wxi.skeleton')
                                   .bytes())
    # Render the WiX template using the MicroDrop version tags, as well as the
    # path to the base directory of the PortablePython distribution to be
    # bundled by the installer.
    wxi_text = wxi_template.render({'major_version': version_tags['major'],
                                    'minor_version': version_tags['minor'],
                                    'build_version': version_tags['post'],
                                    'revision': version_tags['dev'],
                                    'sourcedir': base_dir_path})
    with open(str(target[0]), 'w') as out:
        out.write(wxi_text)
    return None


# Set the MicroDrop package-name to install into the portable Python
# environment.
# __NB__ By default, we use the `--pre` flag to install the latest version of
# `microdrop`, even if it is not a minor version release, _i.e.,_ micro-version
# greater than 0.
default_microdrop_package = 'microdrop --pre'
AddOption('--microdrop-package', dest='microdrop_package', type='string',
          nargs=1, action='store', metavar='MICRODROP_PKG',
          help='`pip`-compatible MicroDrop package reference (default=`%s`)' %
          default_microdrop_package, default=default_microdrop_package)

env = Environment(tools=['default', 'wix', 'unzip', 'url'], ENV=os.environ,
                  MICRODROP_PKG=GetOption('microdrop_package'))

app_env = env.Clone()
app_env.Append(WIXCANDLEFLAGS=['-ext', 'WixUIExtension.dll',
                               '-ext', 'WixUtilExtension.dll'])

# Download `zip` archive containing Portable Python base distribution.
portable_base_zip = env.Download('microdrop_portable_base.zip',
                                 'http://microfluidics.utoronto.ca/downloads/'
                                 'microdrop_portable_base-python_2.7.5.1.zip')

# Extract PortablePython base distribution.
portable_base_dir = env.UnZip('microdrop_portable_base', portable_base_zip)

base_dir_path = path(portable_base_dir[0]).joinpath('base').abspath()

microdrop_package_path = base_dir_path.joinpath('App', 'Lib', 'site-packages',
                                                'microdrop')

# Install the latest version of the `microdrop` Python package available on the
# [Python Package Index][PyPI].
#
# [PyPI]: https://pypi.python.org/pypi
microdrop_python = base_dir_path.joinpath('App', 'python.exe')
pip_microdrop_package = env.Command('dummy', [], '%s '
                                    '%s\App\Scripts\pip-script.py install '
                                    '$MICRODROP_PKG' % (microdrop_python,
                                                        base_dir_path))

wix_header = env.Command('Includes/AppVariables.wxi', pip_microdrop_package,
                         build_wxi)

Depends(pip_microdrop_package, portable_base_dir)
AlwaysBuild(wix_header)
AlwaysBuild(pip_microdrop_package)

# Generate a WiX source file containing references to all files from the
# PortablePython distribution.
files_wxs = app_env.Wxs('Fragments\FilesFragments.wxs', wix_header,
                        WIXHEATFLAGS=
                        ['dir',
                         # The source directory containing files to include
                         # in installer.
                         base_dir_path,
                         # Automatically generate static GUIDs for files.
                         '-ag',
                         # Name component group to name from template.
                         '-cg', 'AppFiles',
                         # Directory reference for destination of files.
                         '-dr', 'INSTALLFOLDER',
                         # Do not include the root directory in the installer.
                         # Only include the _contents_ of the directory.
                         '-srd',
                         # Disable registry harvesting, since this attempts to
                         # find a reference for each `.dll`, etc. in the
                         # scanned files in the system registry.  Any `.dll`
                         # files in this project are Python libraries, and
                         # thus, are not available in the registry.
                         '-sreg'])

# Generate a WiX object file containing the MicroDrop project layout.
# __NB__ This WiX object file does not contain the components corresponding to
# the files from the PortablePython distribution.
app_obj = app_env.WiXObject('MicroDropApp.wixobj', ['App.wxs'])

# Generate a WiX object file containing the PortablePython distribution.
files_obj = env.WiXObject('MicroDropFiles.wixobj', files_wxs)

# Compile a Windows installer installation package from the Wix object files.
installer = app_env.WiX('microdrop-en-us.msi', [app_obj, files_obj],
                        WIXLIGHTFLAGS=['-ext', 'WixUIExtension.dll', '-ext',
                                       'WixUtilExtension.dll', '-b',
                                       base_dir_path, '-cultures:en-us',
                                       '-loc', 'Lang\en-us\Loc_en-us.wxl'])

Depends(app_obj, 'Lang\en-us\Loc_en-us.wxl')
Depends(app_obj, wix_header)
