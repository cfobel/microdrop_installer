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
    wxi_template = jinja2.Template(path('Includes/AppVariables.wxi.skeleton')
                                   .bytes())
    # Render the WiX template using the MicroDrop version tags, as well as the
    # path to the base directory of the PortablePython distribution to be
    # bundled by the installer.
    wxi_text = wxi_template.render({'sourcedir': base_dir_path})
    with open(str(target[0]), 'w') as out:
        out.write(wxi_text)
    return None


env = Environment(tools=['default', 'wix', 'unzip', 'url'], ENV=os.environ)

app_env = env.Clone()
app_env.Append(WIXCANDLEFLAGS=['-ext', 'WixUIExtension.dll',
                               '-ext', 'WixUtilExtension.dll'])

# Set the MicroDrop package-name to install into the portable Python
# environment.
# __NB__ By default, we do not specify a `microdrop` version.  This should
# install the latest *minor* version.
default_microdrop_zip = 'microdrop_portable.zip'
AddOption('--microdrop-zip', dest='microdrop_zip', type='string',
          nargs=1, action='store', metavar='MICRODROP_ZIP',
          help='Name of portable microdrop zip file in `downloads` dir on '
          '`microfluidics.utoronto.ca` (default=`%s`)' %
          default_microdrop_zip, default=default_microdrop_zip)

MICRODROP_ZIP = GetOption('microdrop_zip')
MICRODROP_NAME = path(MICRODROP_ZIP).namebase

# Download `zip` archive containing Portable Python base distribution.
portable_base_zip = env.Download('microdrop_portable.zip',
                                 'http://microfluidics.utoronto.ca/downloads/'
                                 + MICRODROP_ZIP)

# Extract PortablePython base distribution.
portable_base_dir = env.UnZip('microdrop_portable', portable_base_zip)

extracted_root = path(portable_base_dir[0]).expand()
base_dir_path = extracted_root.dirs()[0]

wix_header = env.Command('Includes/AppVariables.wxi', portable_base_dir,
                         build_wxi)

AlwaysBuild(wix_header)

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
