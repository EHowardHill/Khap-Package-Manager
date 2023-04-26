#!/usr/bin/env python

import unittest
from test import support
from test.test_urllib2 import sanepathname2url

import os
import socket
import sys
import urllib.error
import urllib.request


def _retry_thrice(func, exc, *args, **kwargs):
    for i in range(3):
        try:
            return func(*args, **kwargs)
        except exc as e:
            last_exc = e
            continue
        except:
            raise
    raise last_exc

def _wrap_with_retry_thrice(func, exc):
    def wrapped(*args, **kwargs):
        return _retry_thrice(func, exc, *args, **kwargs)
    return wrapped

# Connecting to remote hosts is flaky.  Make it more robust by retrying
# the connection several times.
_urlopen_with_retry = _wrap_with_retry_thrice(urllib.request.urlopen,
                                              urllib.error.URLError)


class AuthTests(unittest.TestCase):
    """Tests urllib2 authentication features."""

## Disabled at the moment since there is no page under python.org which
## could be used to HTTP authentication.
#
#    def test_basic_auth(self):
#        import http.client
#
#        test_url = "http://www.python.org/test/test_urllib2/basic_auth"
#        test_hostport = "www.python.org"
#        test_realm = 'Test Realm'
#        test_user = 'test.test_urllib2net'
#        test_password = 'blah'
#
#        # failure
#        try:
#            _urlopen_with_retry(test_url)
#        except urllib2.HTTPError, exc:
#            self.assertEqual(exc.code, 401)
#        else:
#            self.fail("urlopen() should have failed with 401")
#
#        # success
#        auth_handler = urllib2.HTTPBasicAuthHandler()
#        auth_handler.add_password(test_realm, test_hostport,
#                                  test_user, test_password)
#        opener = urllib2.build_opener(auth_handler)
#        f = opener.open('http://localhost/')
#        response = _urlopen_with_retry("http://www.python.org/")
#
#        # The 'userinfo' URL component is deprecated by RFC 3986 for security
#        # reasons, let's not implement it!  (it's already implemented for proxy
#        # specification strings (that is, URLs or authorities specifying a
#        # proxy), so we must keep that)
#        self.assertRaises(http.client.InvalidURL,
#                          urllib2.urlopen, "http://evil:thing@example.com")


class CloseSocketTest(unittest.TestCase):

    def test_close(self):
        import socket, http.client, gc

        # calling .close() on urllib2's response objects should close the
        # underlying socket

        response = _urlopen_with_retry("http://www.python.org/")
        sock = response.fp
        self.assertTrue(not sock.closed)
        response.close()
        self.assertTrue(sock.closed)

class OtherNetworkTests(unittest.TestCase):
    def setUp(self):
        if 0:  # for debugging
            import logging
            logger = logging.getLogger("test_urllib2net")
            logger.addHandler(logging.StreamHandler())

    # XXX The rest of these tests aren't very good -- they don't check much.
    # They do sometimes catch some major disasters, though.

    def test_ftp(self):
        urls = [
            'ftp://ftp.kernel.org/pub/linux/kernel/README',
            'ftp://ftp.kernel.org/pub/linux/kernel/non-existent-file',
            #'ftp://ftp.kernel.org/pub/leenox/kernel/test',
            'ftp://gatekeeper.research.compaq.com/pub/DEC/SRC'
                '/research-reports/00README-Legal-Rules-Regs',
            ]
        self._test_urls(urls, self._extra_handlers())

    def test_file(self):
        TESTFN = support.TESTFN
        f = open(TESTFN, 'w')
        try:
            f.write('hi there\n')
            f.close()
            urls = [
                'file:' + sanepathname2url(os.path.abspath(TESTFN)),
                ('file:///nonsensename/etc/passwd', None,
                 urllib.error.URLError),
                ]
            self._test_urls(urls, self._extra_handlers(), retry=True)
        finally:
            os.remove(TESTFN)

    # XXX Following test depends on machine configurations that are internal
    # to CNRI.  Need to set up a public server with the right authentication
    # configuration for test purposes.

##     def test_cnri(self):
##         if socket.gethostname() == 'bitdiddle':
##             localhost = 'bitdiddle.cnri.reston.va.us'
##         elif socket.gethostname() == 'bitdiddle.concentric.net':
##             localhost = 'localhost'
##         else:
##             localhost = None
##         if localhost is not None:
##             urls = [
##                 'file://%s/etc/passwd' % localhost,
##                 'http://%s/simple/' % localhost,
##                 'http://%s/digest/' % localhost,
##                 'http://%s/not/found.h' % localhost,
##                 ]

##             bauth = HTTPBasicAuthHandler()
##             bauth.add_password('basic_test_realm', localhost, 'jhylton',
##                                'password')
##             dauth = HTTPDigestAuthHandler()
##             dauth.add_password('digest_test_realm', localhost, 'jhylton',
##                                'password')

##             self._test_urls(urls, self._extra_handlers()+[bauth, dauth])

    def _test_urls(self, urls, handlers, retry=True):
        import socket
        import time
        import logging
        debug = logging.getLogger("test_urllib2").debug

        urlopen = urllib.request.build_opener(*handlers).open
        if retry:
            urlopen = _wrap_with_retry_thrice(urlopen, urllib.error.URLError)

        for url in urls:
            if isinstance(url, tuple):
                url, req, expected_err = url
            else:
                req = expected_err = None
            debug(url)
            try:
                f = urlopen(url, req)
            except EnvironmentError as err:
                debug(err)
                if expected_err:
                    msg = ("Didn't get expected error(s) %s for %s %s, got %s: %s" %
                           (expected_err, url, req, type(err), err))
                    self.assertTrue(isinstance(err, expected_err), msg)
            else:
                with support.time_out, \
                     support.socket_peer_reset, \
                     support.ioerror_peer_reset:
                    buf = f.read()
                f.close()
                debug("read %d bytes" % len(buf))
            debug("******** next url coming up...")
            time.sleep(0.1)

    def _extra_handlers(self):
        handlers = []

        cfh = urllib.request.CacheFTPHandler()
        cfh.setTimeout(1)
        handlers.append(cfh)

        return handlers


class TimeoutTest(unittest.TestCase):
    def test_http_basic(self):
        self.assertTrue(socket.getdefaulttimeout() is None)
        u = _urlopen_with_retry("http://www.python.org")
        self.assertTrue(u.fp.raw._sock.gettimeout() is None)

    def test_http_default_timeout(self):
        self.assertTrue(socket.getdefaulttimeout() is None)
        socket.setdefaulttimeout(60)
        try:
            u = _urlopen_with_retry("http://www.python.org")
        finally:
            socket.setdefaulttimeout(None)
        self.assertEqual(u.fp.raw._sock.gettimeout(), 60)

    def test_http_no_timeout(self):
        self.assertTrue(socket.getdefaulttimeout() is None)
        socket.setdefaulttimeout(60)
        try:
            u = _urlopen_with_retry("http://www.python.org", timeout=None)
        finally:
            socket.setdefaulttimeout(None)
        self.assertTrue(u.fp.raw._sock.gettimeout() is None)

    def test_http_timeout(self):
        u = _urlopen_with_retry("http://www.python.org", timeout=120)
        self.assertEqual(u.fp.raw._sock.gettimeout(), 120)

    FTP_HOST = "ftp://ftp.mirror.nl/pub/mirror/gnu/"

    def test_ftp_basic(self):
        self.assertTrue(socket.getdefaulttimeout() is None)
        u = _urlopen_with_retry(self.FTP_HOST)
        self.assertTrue(u.fp.fp.raw._sock.gettimeout() is None)

    def test_ftp_default_timeout(self):
        self.assertTrue(socket.getdefaulttimeout() is None)
        socket.setdefaulttimeout(60)
        try:
            u = _urlopen_with_retry(self.FTP_HOST)
        finally:
            socket.setdefaulttimeout(None)
        self.assertEqual(u.fp.fp.raw._sock.gettimeout(), 60)

    def test_ftp_no_timeout(self):
        self.assertTrue(socket.getdefaulttimeout() is None)
        socket.setdefaulttimeout(60)
        try:
            u = _urlopen_with_retry(self.FTP_HOST, timeout=None)
        finally:
            socket.setdefaulttimeout(None)
        self.assertTrue(u.fp.fp.raw._sock.gettimeout() is None)

    def test_ftp_timeout(self):
        u = _urlopen_with_retry(self.FTP_HOST, timeout=60)
        self.assertEqual(u.fp.fp.raw._sock.gettimeout(), 60)


def test_main():
    support.requires("network")
    support.run_unittest(AuthTests,
                              OtherNetworkTests,
                              CloseSocketTest,
                              TimeoutTest,
                              )

if __name__ == "__main__":
    test_main()
