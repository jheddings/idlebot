import logging
import unittest

import irc

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


################################################################################
class SocketBufferTest(unittest.TestCase):
    # ---------------------------------------------------------------------------
    def test_BufferSizeCheck(self):
        buf = irc.SocketLineBuffer()

        txt = "simple line of text\n"
        buf += txt.encode()

        self.assertEqual(len(buf), len(txt))
