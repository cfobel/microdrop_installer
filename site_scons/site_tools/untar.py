# -*- coding: UTF8 -*-

import os
import SCons.Node

def UnTarEmitter(target, source, env):
    assert len(target) <= 1 # Until multiple target is managed

    for node in target:
        env.Clean(node, node)

    return target, source


def UnTar(target, source, env):
    import tarfile
    for s in source:
        sourceTar = tarfile.open(s.get_abspath(),'r')
        sourceTar.extractall(path=target[0].get_abspath())
        sourceTar.close()
    return None

def UnTarString(target, source, env):
    """ Information string for UnTar """
    s = 'Extracting %s' % os.path.basename (str (source[0]))
    return env.subst('[${CURRENT_PROJECT}]: ') + s


def generate(env):
    action  = SCons.Action.Action(UnTar, UnTarString)
    builder = env.Builder(
            action         = action,
            emitter        = UnTarEmitter,
            target_factory = env.Dir,
            )

    env.Append(BUILDERS = {'UnTar' : builder})


# existing function of the builder
# @param env environment object
# @return true
def exists(env) :
    return 1
