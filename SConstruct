import os
from subprocess import check_output
from collections import OrderedDict
import re

import jinja2
from path_helpers import path
import wget
import zipfile


portable_base_dir = path('microdrop_portable')
# Check if the portable base folder exists, otherwise download and extract it
if not path(portable_base_dir).exists():
    zip_file_name = path('%s.zip' % portable_base_dir)
    if not zip_file_name.exists():
        print 'Downloading portable python base...'
        wget.download('http://microfluidics.utoronto.ca/downloads/%s' % zip_file_name)
    print "Extracting..."
    with zipfile.ZipFile(zip_file_name, "r") as z:
        z.extractall(portable_base_dir)


def build_wxi(target, source, env):
    '''
    Build WiX header file, defining the application details for the current
    installer build.

    The header includes details such as the Microdrop application version
    number, which is also used as the version number for the installer.
    '''
    wxi_template = jinja2.Template(path('Includes/AppVariables.wxi.skeleton')
                                   .bytes())
    # Render the WiX template using the Microdrop version tags, as well as the
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

base_dir_path = portable_base_dir.dirs()[0]

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

# Generate a WiX object file containing the Microdrop project layout.
# __NB__ This WiX object file does not contain the components corresponding to
# the files from the PortablePython distribution.
app_obj = app_env.WiXObject('MicrodropApp.wixobj', ['App.wxs'])

# Generate a WiX object file containing the PortablePython distribution.
files_obj = env.WiXObject('MicrodropFiles.wixobj', files_wxs)

# Compile a Windows installer installation package from the Wix object files.
installer = app_env.WiX('microdrop-en-us.msi', [app_obj, files_obj],
                        WIXLIGHTFLAGS=['-ext', 'WixUIExtension.dll', '-ext',
                                       'WixUtilExtension.dll', '-b',
                                       base_dir_path, '-cultures:en-us',
                                       '-loc', 'Lang\en-us\Loc_en-us.wxl'])

Depends(app_obj, 'Lang\en-us\Loc_en-us.wxl')
Depends(app_obj, wix_header)
