# -*- coding: koi8-r -*-

import unittest
from test import support

class PEP263Test(unittest.TestCase):

    def test_pep263(self):
        self.assertEqual(
            "�����".encode("utf-8"),
            b'\xd0\x9f\xd0\xb8\xd1\x82\xd0\xbe\xd0\xbd'
        )
        self.assertEqual(
            "\�".encode("utf-8"),
            b'\\\xd0\x9f'
        )

    def test_compilestring(self):
        # see #1882
        c = compile(b"\n# coding: utf-8\nu = '\xc3\xb3'\n", "dummy", "exec")
        d = {}
        exec(c, d)
        self.assertEqual(d['u'], '\xf3')

    def test_issue2301(self):
        try:
            compile(b"# coding: cp932\nprint '\x94\x4e'", "dummy", "exec")
        except SyntaxError as v:
            self.assertEquals(v.text, "print '\u5e74'")
        else:
            self.fail()

    def test_issue4626(self):
        c = compile("# coding=latin-1\n\u00c6 = '\u00c6'", "dummy", "exec")
        d = {}
        exec(c, d)
        self.assertEquals(d['\xc6'], '\xc6')

def test_main():
    support.run_unittest(PEP263Test)

if __name__=="__main__":
    test_main()
