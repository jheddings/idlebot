import logging
import unittest

import irc

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)

# TODO async (multithreaded) append and next test

################################################################################
class LineBufferTest(unittest.TestCase):

    #---------------------------------------------------------------------------
    def test_BasicBufferUsage(self):
        buf = irc.LineBuffer()

        txt = 'simple line of text'

        buf += txt + "\n"

        line = next(buf)
        self.assertEqual(line, txt)

    #---------------------------------------------------------------------------
    def test_VerifyLipsum(self):
        buf = irc.LineBuffer()

        with open('test/lipsum.txt') as fp:
            buf.append(fp.read())

        with open('test/lipsum.txt') as fp:
            for line in fp:
                txtline = line.strip()
                bufline = next(buf)
                self.assertEqual(txtline, bufline)

    #---------------------------------------------------------------------------
    def test_WindowsNewlines(self):
        buf = irc.LineBuffer()

        buf += "this is two\r\nlines of text\r\n"

        line = next(buf)
        self.assertEqual(line, 'this is two')

        line = next(buf)
        self.assertEqual(line, 'lines of text')

        with self.assertRaises(StopIteration):
            line = next(buf)

    #---------------------------------------------------------------------------
    def test_MultilineTextInBuffer(self):
        buf = irc.LineBuffer()

        buf += "this is two\nlines of text\n"

        line = next(buf)
        self.assertEqual(line, 'this is two')

        line = next(buf)
        self.assertEqual(line, 'lines of text')

        with self.assertRaises(StopIteration):
            line = next(buf)

    #---------------------------------------------------------------------------
    def test_MultipartSession(self):
        buf = irc.LineBuffer()

        buf += "this is two\nlines of text\nand part"

        line = next(buf)
        self.assertEqual(line, 'this is two')

        buf += " of a third\nwith a "

        line = next(buf)
        self.assertEqual(line, 'lines of text')

        line = next(buf)
        self.assertEqual(line, 'and part of a third')

        buf += "fourth to wrap things up\n"

        line = next(buf)
        self.assertEqual(line, 'with a fourth to wrap things up')

        with self.assertRaises(StopIteration):
            line = next(buf)

    #---------------------------------------------------------------------------
    def test_MissingEOL(self):
        buf = irc.LineBuffer()

        txt = 'partial line of text'

        with self.assertRaises(StopIteration):
            line = next(buf)

    #---------------------------------------------------------------------------
    def test_BufferLengthTest(self):
        buf = irc.LineBuffer()

        txt = "simple line of text\n"
        buf += txt

        self.assertEqual(len(buf), len(txt))

