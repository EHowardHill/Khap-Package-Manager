import unittest
from test.support import run_unittest
import sys
import warnings


class AllTest(unittest.TestCase):

    def check_all(self, modname):
        names = {}
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", ".* (module|package)",
                                    DeprecationWarning)
            try:
                exec("import %s" % modname, names)
            except ImportError:
                # Silent fail here seems the best route since some modules
                # may not be available in all environments.
                return
        self.assertTrue(hasattr(sys.modules[modname], "__all__"),
                        "%s has no __all__ attribute" % modname)
        names = {}
        exec("from %s import *" % modname, names)
        if "__builtins__" in names:
            del names["__builtins__"]
        keys = set(names)
        all = set(sys.modules[modname].__all__)
        self.assertEqual(keys, all)

    def test_all(self):
        if not sys.platform.startswith('java'):
            # In case _socket fails to build, make this test fail more gracefully
            # than an AttributeError somewhere deep in CGIHTTPServer.
            import _socket

        self.check_all("http.server")
        self.check_all("configparser")
        self.check_all("http.cookies")
        self.check_all("queue")
        self.check_all("socketserver")
        self.check_all("aifc")
        self.check_all("base64")
        self.check_all("bdb")
        self.check_all("binhex")
        self.check_all("calendar")
        self.check_all("collections")
        self.check_all("cgi")
        self.check_all("cmd")
        self.check_all("code")
        self.check_all("codecs")
        self.check_all("codeop")
        self.check_all("colorsys")
        self.check_all("compileall")
        self.check_all("copy")
        self.check_all("copyreg")
        self.check_all("csv")
        self.check_all("dbm.bsd")
        self.check_all("decimal")
        self.check_all("difflib")
        self.check_all("dircache")
        self.check_all("dis")
        self.check_all("doctest")
        self.check_all("_dummy_thread")
        self.check_all("dummy_threading")
        self.check_all("filecmp")
        self.check_all("fileinput")
        self.check_all("fnmatch")
        self.check_all("fpformat")
        self.check_all("ftplib")
        self.check_all("getopt")
        self.check_all("getpass")
        self.check_all("gettext")
        self.check_all("glob")
        self.check_all("gzip")
        self.check_all("heapq")
        self.check_all("http.client")
        self.check_all("ihooks")
        self.check_all("io")
        self.check_all("_pyio")
        self.check_all("imaplib")
        self.check_all("imghdr")
        self.check_all("keyword")
        self.check_all("linecache")
        self.check_all("locale")
        self.check_all("macpath")
        self.check_all("macurl2path")
        self.check_all("mailbox")
        self.check_all("mailcap")
        self.check_all("mhlib")
        self.check_all("mimetypes")
        self.check_all("multifile")
        self.check_all("netrc")
        self.check_all("nntplib")
        self.check_all("ntpath")
        self.check_all("opcode")
        self.check_all("optparse")
        self.check_all("os")
        self.check_all("os2emxpath")
        self.check_all("pdb")
        self.check_all("pickle")
        self.check_all("pickletools")
        self.check_all("pipes")
        self.check_all("poplib")
        self.check_all("posixpath")
        self.check_all("pprint")
        self.check_all("profile")
        self.check_all("pstats")
        self.check_all("pty")
        self.check_all("py_compile")
        self.check_all("pyclbr")
        self.check_all("quopri")
        self.check_all("random")
        self.check_all("re")
        self.check_all("reprlib")
        self.check_all("rlcompleter")
        self.check_all("urllib.robotparser")
        self.check_all("sched")
        self.check_all("shelve")
        self.check_all("shlex")
        self.check_all("shutil")
        self.check_all("smtpd")
        self.check_all("smtplib")
        self.check_all("sndhdr")
        self.check_all("socket")
        self.check_all("_strptime")
        self.check_all("symtable")
        self.check_all("tabnanny")
        self.check_all("tarfile")
        self.check_all("telnetlib")
        self.check_all("tempfile")
        self.check_all("test.support")
        self.check_all("textwrap")
        self.check_all("threading")
        self.check_all("timeit")
        self.check_all("tokenize")
        self.check_all("traceback")
        self.check_all("tty")
        self.check_all("unittest")
        self.check_all("uu")
        self.check_all("warnings")
        self.check_all("wave")
        self.check_all("weakref")
        self.check_all("webbrowser")
        self.check_all("xdrlib")
        self.check_all("zipfile")

        # rlcompleter needs special consideration; it import readline which
        # initializes GNU readline which calls setlocale(LC_CTYPE, "")... :-(
        try:
            self.check_all("rlcompleter")
        finally:
            try:
                import locale
            except ImportError:
                pass
            else:
                locale.setlocale(locale.LC_CTYPE, 'C')


def test_main():
    run_unittest(AllTest)

if __name__ == "__main__":
    test_main()
