# -*- coding: utf-8 -*-
# Test the windows specific win32reg module.
# Only win32reg functions not hit here: FlushKey, LoadKey and SaveKey

import os, sys
import unittest
from test import support

# Do this first so test will be skipped if module doesn't exist
support.import_module('winreg')
# Now import everything
from winreg import *

test_key_name = "SOFTWARE\\Python Registry Test Key - Delete Me"

test_data = [
    ("Int Value",     45,                                      REG_DWORD),
    ("String Val",    "A string value",                        REG_SZ),
    ("StringExpand",  "The path is %path%",                    REG_EXPAND_SZ),
    ("Multi-string",  ["Lots", "of", "string", "values"],      REG_MULTI_SZ),
    ("Raw Data",      b"binary\x00data",                       REG_BINARY),
    ("Big String",    "x"*(2**14-1),                           REG_SZ),
    ("Big Binary",    b"x"*(2**14),                            REG_BINARY),
    # Two and three kanjis, meaning: "Japan" and "Japanese")
    ("Japanese 日本", "日本語", REG_SZ),
]

class WinregTests(unittest.TestCase):
    remote_name = None

    def setUp(self):
        # Make sure that the test key is absent when the test
        # starts.
        self.delete_tree(HKEY_CURRENT_USER, test_key_name)

    def delete_tree(self, root, subkey):
        try:
            hkey = OpenKey(root, subkey, KEY_ALL_ACCESS)
        except WindowsError:
            # subkey does not exist
            return
        while True:
            try:
                subsubkey = EnumKey(hkey, 0)
            except WindowsError:
                # no more subkeys
                break
            self.delete_tree(hkey, subsubkey)
        CloseKey(hkey)
        DeleteKey(root, subkey)

    def WriteTestData(self, root_key, subkeystr="sub_key"):
        # Set the default value for this key.
        SetValue(root_key, test_key_name, REG_SZ, "Default value")
        key = CreateKey(root_key, test_key_name)
        self.assertTrue(key.handle != 0)
        # Create a sub-key
        sub_key = CreateKey(key, subkeystr)
        # Give the sub-key some named values

        for value_name, value_data, value_type in test_data:
            SetValueEx(sub_key, value_name, 0, value_type, value_data)

        # Check we wrote as many items as we thought.
        nkeys, nvalues, since_mod = QueryInfoKey(key)
        self.assertEquals(nkeys, 1, "Not the correct number of sub keys")
        self.assertEquals(nvalues, 1, "Not the correct number of values")
        nkeys, nvalues, since_mod = QueryInfoKey(sub_key)
        self.assertEquals(nkeys, 0, "Not the correct number of sub keys")
        self.assertEquals(nvalues, len(test_data),
                          "Not the correct number of values")
        # Close this key this way...
        # (but before we do, copy the key as an integer - this allows
        # us to test that the key really gets closed).
        int_sub_key = int(sub_key)
        CloseKey(sub_key)
        try:
            QueryInfoKey(int_sub_key)
            self.fail("It appears the CloseKey() function does "
                      "not close the actual key!")
        except EnvironmentError:
            pass
        # ... and close that key that way :-)
        int_key = int(key)
        key.Close()
        try:
            QueryInfoKey(int_key)
            self.fail("It appears the key.Close() function "
                      "does not close the actual key!")
        except EnvironmentError:
            pass

    def ReadTestData(self, root_key, subkeystr="sub_key"):
        # Check we can get default value for this key.
        val = QueryValue(root_key, test_key_name)
        self.assertEquals(val, "Default value",
                          "Registry didn't give back the correct value")

        key = OpenKey(root_key, test_key_name)
        # Read the sub-keys
        with OpenKey(key, subkeystr) as sub_key:
            # Check I can enumerate over the values.
            index = 0
            while 1:
                try:
                    data = EnumValue(sub_key, index)
                except EnvironmentError:
                    break
                self.assertEquals(data in test_data, True,
                                  "Didn't read back the correct test data")
                index = index + 1
            self.assertEquals(index, len(test_data),
                              "Didn't read the correct number of items")
            # Check I can directly access each item
            for value_name, value_data, value_type in test_data:
                read_val, read_typ = QueryValueEx(sub_key, value_name)
                self.assertEquals(read_val, value_data,
                                  "Could not directly read the value")
                self.assertEquals(read_typ, value_type,
                                  "Could not directly read the value")
        sub_key.Close()
        # Enumerate our main key.
        read_val = EnumKey(key, 0)
        self.assertEquals(read_val, subkeystr, "Read subkey value wrong")
        try:
            EnumKey(key, 1)
            self.fail("Was able to get a second key when I only have one!")
        except EnvironmentError:
            pass

        key.Close()

    def DeleteTestData(self, root_key, subkeystr="sub_key"):
        key = OpenKey(root_key, test_key_name, 0, KEY_ALL_ACCESS)
        sub_key = OpenKey(key, subkeystr, 0, KEY_ALL_ACCESS)
        # It is not necessary to delete the values before deleting
        # the key (although subkeys must not exist).  We delete them
        # manually just to prove we can :-)
        for value_name, value_data, value_type in test_data:
            DeleteValue(sub_key, value_name)

        nkeys, nvalues, since_mod = QueryInfoKey(sub_key)
        self.assertEquals(nkeys, 0, "subkey not empty before delete")
        self.assertEquals(nvalues, 0, "subkey not empty before delete")
        sub_key.Close()
        DeleteKey(key, subkeystr)

        try:
            # Shouldnt be able to delete it twice!
            DeleteKey(key, subkeystr)
            self.fail("Deleting the key twice succeeded")
        except EnvironmentError:
            pass
        key.Close()
        DeleteKey(root_key, test_key_name)
        # Opening should now fail!
        try:
            key = OpenKey(root_key, test_key_name)
            self.fail("Could open the non-existent key")
        except WindowsError: # Use this error name this time
            pass

    def TestAll(self, root_key, subkeystr="sub_key"):
        self.WriteTestData(root_key, subkeystr)
        self.ReadTestData(root_key, subkeystr)
        self.DeleteTestData(root_key, subkeystr)

    def testLocalMachineRegistryWorks(self):
        self.TestAll(HKEY_CURRENT_USER)
        self.TestAll(HKEY_CURRENT_USER, "日本-subkey")

    def testConnectRegistryToLocalMachineWorks(self):
        # perform minimal ConnectRegistry test which just invokes it
        h = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        h.Close()

    def testRemoteMachineRegistryWorks(self):
        if not self.remote_name:
            return # remote machine name not specified
        remote_key = ConnectRegistry(self.remote_name, HKEY_CURRENT_USER)
        self.TestAll(remote_key)

    def testExpandEnvironmentStrings(self):
        r = ExpandEnvironmentStrings("%windir%\\test")
        self.assertEqual(type(r), str)
        self.assertEqual(r, os.environ["windir"] + "\\test")

def test_main():
    support.run_unittest(WinregTests)

if __name__ == "__main__":
    try:
        WinregTests.remote_name = sys.argv[sys.argv.index("--remote")+1]
    except (IndexError, ValueError):
        print("Remote registry calls can be tested using",
              "'test_winreg.py --remote \\\\machine_name'")
        WinregTests.remote_name = None
    test_main()
