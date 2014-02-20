# -*- coding: UTF8 -*-

import os
import SCons.Node


def UnZipEmitter(target, source, env):
    assert len(target) <= 1 # Until multiple target is managed

    for node in target:
        env.Clean(node, node)

    return target, source


def UnZip(target, source, env):
    import zipfile
    for s in source:
        sourceZip = zipfile.ZipFile(s.get_abspath(),'r')
        sourceZip.extractall(path=target[0].get_abspath())
        sourceZip.close()
    return None

def UnZipString(target, source, env):
    """ Information string for UnZip """
    s = 'Extracting %s' % os.path.basename (str (source[0]))
    return env.subst('[${CURRENT_PROJECT}]: ') + s


def generate(env):
    action  = SCons.Action.Action(UnZip, UnZipString)
    builder = env.Builder(
            action         = action,
            emitter        = UnZipEmitter,
            target_factory = env.Dir,
            )

    env.Append(BUILDERS = {'UnZip' : builder})


# existing function of the builder
# @param env environment object
# @return true
def exists(env) :
    return 1
