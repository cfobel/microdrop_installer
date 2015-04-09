# -*- coding: UTF8 -*-

import sys
import string
import UserDict

import SCons.Node
import SCons.Util

import urllib2
from urlparse import urlparse

class UrlNameSpace(UserDict.UserDict):
    def Url(self, name, **kw):
        if isinstance(name, Url):
            return name
        try:
            a = self[name]
        except KeyError:
            a = apply(Url, (name,), kw)
            self[name] = a
        return a

    def lookup(self, name, **kw):
        try:
            return self[name]
        except KeyError:
            return None

class UrlNodeInfo(SCons.Node.NodeInfoBase):
    current_version_id = 1
    field_list = ['csig']
    def str_to_node(self, s):
        return default_uns.Url(s)

class UrlBuildInfo(SCons.Node.BuildInfoBase):
    current_version_id = 1

class Url(SCons.Node.Node):

    NodeInfo = UrlNodeInfo
    BuildInfo = UrlBuildInfo

    def __init__(self, url):
        SCons.Node.Node.__init__(self)
        self.name = url

    def str_for_display(self):
        return '"' + self.__str__() + '"'

    def __str__(self):
        return self.name

    def make_ready(self):
        self.get_csig()

    really_build = SCons.Node.Node.build
    is_up_to_date = SCons.Node.Node.children_are_up_to_date

    def is_under(self, dir):
        # Make Url nodes get built regardless of
        # what directory scons was run from. Url nodes
        # are outside the filesystem:
        return 1

    def get_contents(self):
        """The contents of an url is the concatenation
        of the content signatures of all its sources."""
        childsigs = map(lambda n: n.get_csig(), self.children())
        return string.join(childsigs, '')

    def sconsign(self):
        """An Url is not recorded in .sconsign files"""
        pass


    def changed_since_last_build(self, target, prev_ni):
        cur_csig = self.get_csig()
        try:
            return cur_csig != prev_ni.csig
        except AttributeError:
            return 1

    def build(self):
        """A "builder" for Url."""
        pass

    def convert(self):
        try: del self.builder
        except AttributeError: pass
        self.reset_executor()
        self.build = self.really_build

    def get_csig(self):
        """
        Generate a node's content signature, the digested signature
        of its content.

        node - the node
        cache - alternate node to use for the signature cache
        returns - the content signature
        """
        try:
            return self.ninfo.csig
        except AttributeError:
            pass

        contents = self.get_contents()
        csig = SCons.Util.MD5signature(contents)
        self.get_ninfo().csig = csig
        return csig

    def exists(self):
        return True


def check_url(url):
    pieces = urlparse(url)
    if not all([pieces.scheme, pieces.netloc]):
        raise Exception, 'Malformed Url: "{0}"'.format(url)
    return True



def download_file(url, io, output_path):
    # TODO: Fix `download_file` implementation _(taken from
    # `install_dependencies.py`)_.  Use to download Microdrop custom
    # PortablePython distribution, currently located in `/home/christian` on
    # `microfluidics.utoronto.ca`.
    downloaded = 0
    print url
    with open(output_path, 'wb') as output:
        total_length = None
        try:
            if io.info().getheaders("Content-Length"):
                total_length = int(io.info().getheaders("Content-Length")[0])
                print('Downloading %s (%s kB): ' % (url, total_length >> 10))
            else:
                print('Downloading %s (unknown size): ' % url)
            while True:
                chunk = io.read(4096)
                if not chunk:
                    break
                downloaded += len(chunk)
                if not total_length:
                    sys.stdout.write('\r%s kB' % (downloaded >> 10))
                else:
                    sys.stdout.write('\r%3i%%  %s kB' % (100 * downloaded /
                                                         total_length,
                                                         downloaded >> 10))
                sys.stdout.flush()
                output.write(chunk)
        finally:
            sys.stdout.write('\n');
            sys.stdout.flush()


def Download(target, source, env):
    if not len(target) == 1:
        raise Exception, (
                "Number of target ({0}) must be equal 1".format(len(target))
                )

    if not len(source) > 0:
        raise Exception, (
                "'Download'"
                " takes at least one url as source.".format(len(source))
                )

    t = target[0]
    urls = source
    stream = None
    for url in urls:
        url = url.name
        try:
            check_url(url)
            stream = urllib2.urlopen(url, timeout=10)
            break
        except urllib2.URLError, e:
            print 'Download failed : %s: %s. Trying next url...' % (url, str(e))

    if stream is None:
        raise Exception, ('Was not able to retrieve any of {0}'.format(urls))

    download_file(url, stream, t.get_path())
    stream.close()

    return None


def DownloadString(target, source, env):
    s = ' Downloading %s' % target[0]
    return env.subst('[${CURRENT_PROJECT}]: ') + s


def generate(env):
    env.Url = Url
    SCons.Node.FS.get_default_fs().Url = Url
    action = SCons.Action.Action(Download, DownloadString)
    builder = env.Builder(
            action=action ,
            source_factory = Url,
            )

    env.Append(BUILDERS = {'Download' : builder})


# existing function of the builder
# @param env environment object
# @return true
def exists(env) :
    return 1


default_uns = UrlNameSpace()

SCons.Node.arg2nodes_lookups.append(default_uns.lookup)
