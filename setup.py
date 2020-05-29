#!/usr/bin/env python
import os.path
import shlex
import shutil
import subprocess
import sys
import urllib.request
from distutils.file_util import copy_file
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as setuptools_build_ext

class xapian_build_ext(setuptools_build_ext):
    def xapian_download(self, fname, url):
        if os.access(fname, os.F_OK):
            print('already downloaded', fname)
            return
        print('downloading', fname, 'from', url)
        if self.dry_run:
            return
        with open(fname + ".tmp", 'wb') as dstf:
            with urllib.request.urlopen(url) as srcf:
                shutil.copyfileobj(srcf, dstf)
        os.rename(fname + ".tmp", fname)

    def xapian_extract(self, tarball, dst):
        if os.access(dst, os.F_OK):
            print('already extracted', dst)
            return
        print('extracting', dst, 'from', tarball)
        if not self.dry_run:
            os.makedirs(dst + ".tmp", exist_ok=True)
            subprocess.run(["tar", "-C", dst + ".tmp", "-xaf", tarball, "--strip-components=1"], check=True)
            os.rename(dst + ".tmp", dst)

    def xapian_run(self, *args, **kwargs):
        print("executing", ' '.join(shlex.quote(arg) for arg in args))
        if not self.dry_run:
            subprocess.run(args, **kwargs, check=True)

    def xapian_cd(self, dirname):
        print("chdir", dirname)
        if not self.dry_run:
            os.chdir(dirname)

    def run(self):
        old_cwd = os.getcwd()
        tmpdir = os.path.abspath(self.build_temp)
        os.makedirs(tmpdir, exist_ok=True)
        try:
            self.xapian_cd(tmpdir)
            fmtargs = {'version': self.distribution.get_version().split('+', 1)[0]}
            self.xapian_download('xapian-core.tar.xz', "https://oligarchy.co.uk/xapian/%(version)s/xapian-core-%(version)s.tar.xz" % fmtargs)
            self.xapian_download('xapian-bindings.tar.xz', "https://oligarchy.co.uk/xapian/%(version)s/xapian-bindings-%(version)s.tar.xz" % fmtargs)
            self.xapian_extract('xapian-core.tar.xz', 'xapian-core')
            self.xapian_extract('xapian-bindings.tar.xz', 'xapian-bindings')
            self.xapian_cd(os.path.join(tmpdir, "xapian-core"))
            if self.dry_run or not os.access("config.status", os.F_OK):
                self.xapian_run("./configure")
            self.xapian_run("make", "-j" + str(self.parallel if self.parallel else os.cpu_count()))
            self.xapian_cd(os.path.join(tmpdir, "xapian-bindings"))
            os.putenv("XAPIAN_CONFIG", os.path.join(tmpdir, "xapian-core", "xapian-config"))
            os.putenv("LDFLAGS", "-Wl,-rpath,'$$ORIGIN'")
            os.putenv("PYTHON3", sys.executable)
            if self.dry_run or not os.access("config.status", os.F_OK):
                self.xapian_run("sed", "-i", "s!import sphinx!import sys!g", "configure")
                self.xapian_run("./configure", "--with-python3")
            with open('python3/Makefile.py3ext', 'w') as makef:
                makef.write('include Makefile\n')
                makef.write('py3ext: xapian/_xapian$(PYTHON3_SO) xapian/__init__.py\n')
                makef.write('.PHONY: py3ext\n')
            self.xapian_run("make", "-C", "python3", "-f", "Makefile.py3ext", "-j" + str(self.parallel if self.parallel else os.cpu_count()), "py3ext")
            xapian_lib_path = os.path.join(tmpdir, "xapian-core", ".libs", xapian_lib_name)
        finally:
            self.xapian_cd(old_cwd)
        temp_ext_dir = os.path.join(tmpdir, 'xapian-bindings', 'python3', 'xapian')
        build_ext_dir = os.path.join(self.build_lib, 'xapian')
        if not self.dry_run:
            os.makedirs(build_ext_dir, exist_ok=True)
        copy_file(os.path.join(temp_ext_dir, self.get_ext_filename('_xapian')), build_ext_dir)
        copy_file(os.path.join(temp_ext_dir, '__init__.py'), build_ext_dir)
        copy_file(xapian_lib_path, build_ext_dir)

xapian_lib_name = "libxapian.so.30"

setup(
    name='xapian',
    version='1.4.15+1',
    description='Python bindings for Xapian',
    packages=['xapian'],
    ext_modules=[Extension('xapian._xapian', [])],
    cmdclass={'build_ext': xapian_build_ext},
)
