# coding=utf-8
import main
from mock import patch, Mock
import unittest
import os.path
import elementtree.ElementTree as ElTr
import xml.etree.ElementTree as elTree

from main import get_mp3_info, download_mp3, get_links, search_mp3_links, \
    get_references, write_xml


class ScriptTest(unittest.TestCase):
    def test_get_mp3_info(self):
        self.assertEqual(get_mp3_info(''), {}, "Check wrong file path!")
        song = 'mp3s//Test_song1.mp3'
        if os.path.isfile(song):
            self.assertIsNotNone(get_mp3_info(song))
            tpl = get_mp3_info(song)
            self.assertTrue('artist' in tpl or 'title' in tpl or
                            'album' in tpl or 'genre' in tpl,
                            "Check for music song")

    @patch('main.urllib.urlopen')
    def test_download_mp3(self, mock_urlopen):
        a = Mock()
        a.read.side_effect = []
        mock_urlopen.return_value = a
        res = main.download_mp3('', 'Test_song')
        assert not res

        a.read.side_effect = []
        mock_urlopen.return_value = a
        res = main.download_mp3('https://ia902508.us.archive.org/5/items/testmp3testfile/mpthreetest.mp3', '')
        assert not res

    @patch('main.urllib.urlopen')
    def test_download2_mp3(self, mock_urlopen):

        a = Mock()
        a.read.side_effect = ['Something']
        mock_urlopen.return_value = a
        res = main.download_mp3('https://ia902508.us.archive.org/5/items/testmp3testfile/mpthreetest.mp3',
                                'Test_song')
        assert res

    def test_write_xml(self):
        self.assertIsNone(write_xml([]))

        path = "files//test_write.xml"
        t1 = {"artist": 'artist1', "album": 'album1',
              "title": 'title1', "genre": 'genre1'}
        t2 = {}
        write_xml([t1], path)

        root = ElTr.parse(path).getroot()
        for child in root:
            for child2 in child:
                t2[child2.tag] = child2.text
        self.assertEqual(t1, t2)

    def test_get_references(self):
        self.assertEqual(get_references(''), [], "Check for empty!")
        path = "files//test_get_references.xml"
        write_xml([{"refer": "anything1"}], path)
        self.assertEqual(get_references(path), [])

    @patch('main.urllib.urlopen')
    def test_get_links(self, mock_urlopen):
        a = Mock()
        l = []
        a.side_effect = []
        mock_urlopen.return_value = a
        main.get_links('http://some_site.com.ua', 0, l)
        assert l.__contains__('http://some_site.com.ua')

    @patch('main.urllib.urlopen')
    def test_search_mp3_links(self, mock_urlopen):
        a = Mock()
        l = []
        with open('test//Test_html.txt', 'r') as f:
            html_page = f.read()
            a.side_effect = html_page
            mock_urlopen.return_value = a
            main.search_mp3_links('http://mp3juices.to/mp3/evanescence', l)
            assert l

        l = []
        a.side_effect = ''
        mock_urlopen.return_value = a
        main.search_mp3_links('', l)
        assert not l


if __name__ == '__main__':
    unittest.main()