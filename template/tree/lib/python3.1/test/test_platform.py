import sys
import os
import unittest
import platform
import subprocess

from test import support

class PlatformTest(unittest.TestCase):
    def test_architecture(self):
        res = platform.architecture()

    if hasattr(os, "symlink"):
        def test_architecture_via_symlink(self): # issue3762
            def get(python):
                cmd = [python, '-c',
                    'import platform; print(platform.architecture())']
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                return p.communicate()
            real = os.path.realpath(sys.executable)
            link = os.path.abspath(support.TESTFN)
            os.symlink(real, link)
            try:
                self.assertEqual(get(real), get(link))
            finally:
                os.remove(link)

    def test_platform(self):
        for aliased in (False, True):
            for terse in (False, True):
                res = platform.platform(aliased, terse)

    def test_system(self):
        res = platform.system()

    def test_node(self):
        res = platform.node()

    def test_release(self):
        res = platform.release()

    def test_version(self):
        res = platform.version()

    def test_machine(self):
        res = platform.machine()

    def test_processor(self):
        res = platform.processor()

    def setUp(self):
        self.save_version = sys.version
        self.save_subversion = sys.subversion
        self.save_platform = sys.platform

    def tearDown(self):
        sys.version = self.save_version
        sys.subversion = self.save_subversion
        sys.platform = self.save_platform

    def test_sys_version(self):
        # Old test.
        for input, output in (
            ('2.4.3 (#1, Jun 21 2006, 13:54:21) \n[GCC 3.3.4 (pre 3.3.5 20040809)]',
             ('CPython', '2.4.3', '', '', '1', 'Jun 21 2006 13:54:21', 'GCC 3.3.4 (pre 3.3.5 20040809)')),
            ('IronPython 1.0.60816 on .NET 2.0.50727.42',
             ('IronPython', '1.0.60816', '', '', '', '', '.NET 2.0.50727.42')),
            ('IronPython 1.0 (1.0.61005.1977) on .NET 2.0.50727.42',
             ('IronPython', '1.0.0', '', '', '', '', '.NET 2.0.50727.42')),
            ):
            # branch and revision are not "parsed", but fetched
            # from sys.subversion.  Ignore them
            (name, version, branch, revision, buildno, builddate, compiler) \
                   = platform._sys_version(input)
            self.assertEqual(
                (name, version, '', '', buildno, builddate, compiler), output)

        # Tests for python_implementation(), python_version(), python_branch(),
        # python_revision(), python_build(), and python_compiler().
        sys_versions = {
            ("2.6.1 (r261:67515, Dec  6 2008, 15:26:00) \n[GCC 4.0.1 (Apple Computer, Inc. build 5370)]",
             ('CPython', 'tags/r261', '67515'), self.save_platform)
            :
                ("CPython", "2.6.1", "tags/r261", "67515",
                 ('r261:67515', 'Dec  6 2008 15:26:00'),
                 'GCC 4.0.1 (Apple Computer, Inc. build 5370)'),
            ("IronPython 2.0 (2.0.0.0) on .NET 2.0.50727.3053", None, "cli")
            :
                ("IronPython", "2.0.0", "", "", ("", ""),
                 ".NET 2.0.50727.3053"),
            ("2.5 (trunk:6107, Mar 26 2009, 13:02:18) \n[Java HotSpot(TM) Client VM (\"Apple Computer, Inc.\")]",
            ('Jython', 'trunk', '6107'), "java1.5.0_16")
            :
                ("Jython", "2.5.0", "trunk", "6107",
                 ('trunk:6107', 'Mar 26 2009'), "java1.5.0_16"),
            ("2.5.2 (63378, Mar 26 2009, 18:03:29)\n[PyPy 1.0.0]",
             ('PyPy', 'trunk', '63378'), self.save_platform)
            :
                ("PyPy", "2.5.2", "trunk", "63378", ('63378', 'Mar 26 2009'),
                 "")
            }
        for (version_tag, subversion, sys_platform), info in \
                sys_versions.items():
            sys.version = version_tag
            if subversion is None:
                if hasattr(sys, "subversion"):
                    del sys.subversion
            else:
                sys.subversion = subversion
            if sys_platform is not None:
                sys.platform = sys_platform
            self.assertEqual(platform.python_implementation(), info[0])
            self.assertEqual(platform.python_version(), info[1])
            self.assertEqual(platform.python_branch(), info[2])
            self.assertEqual(platform.python_revision(), info[3])
            self.assertEqual(platform.python_build(), info[4])
            self.assertEqual(platform.python_compiler(), info[5])

    def test_system_alias(self):
        res = platform.system_alias(
            platform.system(),
            platform.release(),
            platform.version(),
        )

    def test_uname(self):
        res = platform.uname()
        self.assertTrue(any(res))

    def test_java_ver(self):
        res = platform.java_ver()
        if sys.platform == 'java':
            self.assertTrue(all(res))

    def test_win32_ver(self):
        res = platform.win32_ver()

    def test_mac_ver(self):
        res = platform.mac_ver()

        if platform.uname()[0] == 'Darwin':
            # We're on a MacOSX system, check that
            # the right version information is returned
            fd = os.popen('sw_vers', 'r')
            real_ver = None
            for ln in fd:
                if ln.startswith('ProductVersion:'):
                    real_ver = ln.strip().split()[-1]
                    break
            fd.close()
            self.assertFalse(real_ver is None)
            self.assertEquals(res[0], real_ver)

            # res[1] claims to contain
            # (version, dev_stage, non_release_version)
            # That information is no longer available
            self.assertEquals(res[1], ('', '', ''))

            if sys.byteorder == 'little':
                self.assertEquals(res[2], 'i386')
            else:
                self.assertEquals(res[2], 'PowerPC')

    def test_dist(self):
        res = platform.dist()

    def test_libc_ver(self):
        import os
        if os.path.isdir(sys.executable) and \
           os.path.exists(sys.executable+'.exe'):
            # Cygwin horror
            executable = executable + '.exe'
        res = platform.libc_ver(sys.executable)

    def test_parse_release_file(self):

        for input, output in (
            # Examples of release file contents:
            ('SuSE Linux 9.3 (x86-64)', ('SuSE Linux ', '9.3', 'x86-64')),
            ('SUSE LINUX 10.1 (X86-64)', ('SUSE LINUX ', '10.1', 'X86-64')),
            ('SUSE LINUX 10.1 (i586)', ('SUSE LINUX ', '10.1', 'i586')),
            ('Fedora Core release 5 (Bordeaux)', ('Fedora Core', '5', 'Bordeaux')),
            ('Red Hat Linux release 8.0 (Psyche)', ('Red Hat Linux', '8.0', 'Psyche')),
            ('Red Hat Linux release 9 (Shrike)', ('Red Hat Linux', '9', 'Shrike')),
            ('Red Hat Enterprise Linux release 4 (Nahant)', ('Red Hat Enterprise Linux', '4', 'Nahant')),
            ('CentOS release 4', ('CentOS', '4', None)),
            ('Rocks release 4.2.1 (Cydonia)', ('Rocks', '4.2.1', 'Cydonia')),
            ):
            self.assertEqual(platform._parse_release_file(input), output)


def test_main():
    support.run_unittest(
        PlatformTest
    )

if __name__ == '__main__':
    test_main()
