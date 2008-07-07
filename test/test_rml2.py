# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Henry Obein <henry@itaapy.com>
# Copyright (C) 2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library
import unittest

# Import from itools
from itools.pdf import (rml2topdf_test, normalize, paragraph_stream,
                        getSampleStyleSheet)
from itools.xml import XMLParser


class FunctionTestCase(unittest.TestCase):

    def test_normalize(self):
        s = ''
        _s = normalize(s)
        self.assertEqual(_s, u'')

        s = ' '
        _s = normalize(s)
        self.assertEqual(_s, u'')

        s = '\t \t   foo \t \t is \t \t \t not \t      \t bar \t \t \t'
        _s = normalize(s)
        self.assertEqual(_s, u'foo is not bar')

        s = 'Hello \t &nbsp; \t Jo'
        _s = normalize(s)
        self.assertEqual(_s, u'Hello &nbsp; Jo')


    def test_formatting(self):
        data = '<p>TXT <i>TEXT<u>TEXT</u></i></p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        self.assertEqual(p.text, '<para>TXT <i>TEXT<u>TEXT</u></i></para>')

        data = '<p>TXT <i>TEXT<u>TEXT</u>TEXT</i></p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        goodanswer = '<para>TXT <i>TEXT<u>TEXT</u>TEXT</i></para>'
        self.assertEqual(p.text, goodanswer)

        data = '<p>TXT <i>TEXT<u>TEXT</u></i>TEXT</p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        goodanswer = '<para>TXT <i>TEXT<u>TEXT</u></i>TEXT</para>'
        self.assertEqual(p.text, goodanswer)

        data = '<p>TXT <i>TEXT<u>TEXT</u>TEXT</i>TEXT</p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        goodanswer = '<para>TXT <i>TEXT<u>TEXT</u>TEXT</i>TEXT</para>'
        self.assertEqual(p.text, goodanswer)

        data = '<p>TXT <i><u>TXT</u></i></p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        self.assertEqual(p.text, '<para>TXT <i><u>TXT</u></i></para>')

        data = '<p><i>TEXT<u>TEXT</u></i></p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        self.assertEqual(p.text, '<para><i>TEXT<u>TEXT</u></i></para>')

        data = '<p><i>TEXT<u>TEXT</u>TEXT</i></p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        self.assertEqual(p.text, '<para><i>TEXT<u>TEXT</u>TEXT</i></para>')

        data = '<p><i>TEXT<u>TEXT</u></i>TEXT</p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        self.assertEqual(p.text, '<para><i>TEXT<u>TEXT</u></i>TEXT</para>')

        data = '<p><i>TEXT<u>TEXT</u>TEXT</i>TEXT</p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        goodanswer = '<para><i>TEXT<u>TEXT</u>TEXT</i>TEXT</para>'
        self.assertEqual(p.text, goodanswer)

        data = '<p><i><u>TXT</u></i></p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        self.assertEqual(p.text, '<para><i><u>TXT</u></i></para>')

        data = '<p>TEXT<sup>TEXT</sup></p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        self.assertEqual(p.text, '<para>TEXT<super>TEXT</super></para>')


    def test_formatting_using_span(self):
        data = '<p><span style="color: #FF9000">clear syntax</span></p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        goodanswer = '<para><font color="#ff9000">clear syntax</font></para>'
        self.assertEqual(p.text, goodanswer)

        data = '<p>essai<span style="color: rgb(255, 0, 0);"> essai essai'
        data += '</span>essai</p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        goodanswer = '<para>essai<font color="#ff0000"> essai essai'
        goodanswer += '</font>essai</para>'
        self.assertEqual(p.text, goodanswer)

        data = '<p>essai <span style="color: rgb(0, 255, 0);">essai essai'
        data += '</span>essai</p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        goodanswer = '<para>essai <font color="#00ff00">essai essai'
        goodanswer += '</font>essai</para>'
        self.assertEqual(p.text, goodanswer)

        data = '<p>essai <span style="color: rgb(0, 0, 255);">essai '
        data += 'essai</span> essai</p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        goodanswer = '<para>essai <font color="#0000ff">essai essai</font>'
        goodanswer += ' essai</para>'
        self.assertEqual(p.text, goodanswer)

        data = '<p>Span <span style="color: rgb(255, 0, 0);">span    span '
        data += '<span style="color: #00DD45;">span</span> span</span>.</p>'
        stream = XMLParser(data)
        stream.next()
        p = paragraph_stream(stream, 'p', {}, getSampleStyleSheet())
        goodanswer = '<para>Span <font color="#ff0000">span span <font '
        goodanswer += 'color="#00dd45">span</font> span</font>.</para>'
        self.assertEqual(p.text, goodanswer)



class HtmlTestCase(unittest.TestCase):


    def test_empty_body(self):
        data = '<html><body></body></html>'
        story, stylesheet = rml2topdf_test(data, raw=True)
        self.assertEqual(len(story), 0)

    def test_paragraph1(self):
        data = '<html><body><p>hello  world</p></body></html>'
        story, stylesheet = rml2topdf_test(data, raw=True)
        self.assertEqual(len(story), 1)


    def test_paragraph2(self):
        data = '<html><body><h1>title</h1><p>hello  world</p>'
        data += '<h2>subtitle1</h2><p>Hello</p><h2>subtitle 2</h2>'
        data += '<p>WORLD     <br/>       </p>;)</body></html>'
        story, stylesheet = rml2topdf_test(data, raw=True)
        self.assertEqual(len(story), 6)


    def test_paragraph3(self):
        story, stylesheet = rml2topdf_test('rml2/paragraph.xml')
        self.assertEqual(len(story), 10)


    def test_list(self):
        story, stylesheet = rml2topdf_test('rml2/list.xml')
        self.assertEqual(len(story), 184)


    def test_image(self):
        data = """
        <html>
            <body>
                <p>hello  world <img src="pdf/itaapy.gif" alt="itaapy" /></p>
                <img src="pdf/itaapy.jpeg" alt="itaapy" />
                <p><img src="pdf/itaapy.png" alt="itaapy" /></p>
            </body>
        </html>"""
        story, stylesheet = rml2topdf_test(data, raw=True)
        self.assertEqual(len(story), 3)


    def test_table(self):
        story, stylesheet = rml2topdf_test('rml2/table.xml')
        self.assertEqual(len(story), 1)



if __name__ == '__main__':
    unittest.main()