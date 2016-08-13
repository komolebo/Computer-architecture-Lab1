# coding=utf-8
import re
import httplib
import urllib2
import urllib
import xml.etree.ElementTree as elTree
from BeautifulSoup import BeautifulSoup
from urllib2 import HTTPError

import eyed3
import elementtree.ElementTree as ElTr
import time
import gevent


def get_mp3_info(filename):  # Отримує посилання на файл та
    d_song = {}              # виводить мета-дані про mp3-файл
    try:
        tag = eyed3.load(filename).tag
        d_song['album'] = tag.album
        d_song['title'] = tag.title
        d_song['artist'] = tag.artist
        d_song['genre'] = tag.genre.name
    except AttributeError:
        pass
    except eyed3.Error:
        pass
    except IOError:
        pass
    return d_song


def download_mp3(url_, filename):  # Бере url-адрес mp3-файлу та закачує
    try:                           # його в директорію, вказану в filename
        data_ = urllib.urlopen(url_).read()
        song = open("mp3s//" + filename + ".mp3", "wb")
        song.write(data_)
        song.close()
        return True
    except HTTPError:
        return False
    except StopIteration:
        return False
    except IOError:
        return False


# Рекурсивно пробігається по посиланнях заданої вкладеності level
def get_links(url_, level, data_):
    # отримує url сайту та локальну url адресу певної вкладки
    print "level ", level, ": ", url_
    # основна url адреса необхідна для рекурсивного проходу
    data_.append(url_)
    if level > 0:  # умова зупинки рекурсії
        try:
            soup_ = BeautifulSoup(urllib2.urlopen(url_))
            for link in soup_.findAll('a'):
                if link['href'].__contains__("http"):  # якщо є посилання
                    get_links(link['href'], level - 1, data_)
        except HTTPError:  # якщо заданий сайт не існує або не працює
            print url_, " not found"
        except KeyError:  # якщо атрибуту 'href' немає
            print "KeyError"


# по заданій url-адресі шукає із веб-сторінки всі посилання на .mp3
def search_mp3_links(url_, data_):
    print "Searching mp3 in " + url_
    try:
        html_page = urllib2.urlopen(url_)  # закачуємо весь html-файл
        soup_ = BeautifulSoup(html_page)
        # використовуємо регулярні вирази для пошуку
        for link in soup_.findAll('a', href=re.compile('.*\.mp3')):
            data_.append(link['href'])
            print "found mp3-link: " + link['href']
    except HTTPError:  # якщо заданий сайт не існує або не працює
        print "HTTPErro caught"
    except urllib2.URLError:            # якщо зєднання переривається
        print "URLError error caught"   # або відсутній доступ до файлу
    except httplib.InvalidURL:  # якщо неправильна адреса
        print "InvalidURL caught"
    except ValueError:
        pass


# бере усі посилання, які ми вказали в xml-файлі
def get_references(ref_filename=".//files//references.xml"):
    try:
        sites = []  # всі сайти для майбутнього проходу
        tree = ElTr.parse(ref_filename)
        mp3_file = tree.findall('.//refer')  # сайти містяться в тегах refer
        for link in mp3_file:
            sites.append(link.text)
        return sites
    except IOError:
        return []


def write_xml(d_data, filename=".//files//output.xml"):  # Запис xml із списку
    root = elTree.Element("root")
    for song in d_data:
        try:
            elem = elTree.SubElement(root, "song")
            elTree.SubElement(elem, "artist").text = song['artist']
            elTree.SubElement(elem, "album").text = song['album']
            elTree.SubElement(elem, "title").text = song['title']
            elTree.SubElement(elem, "genre").text = song['genre']
        except KeyError:  # якщо певного атрибуту немає
            pass
    tree = elTree.ElementTree(root)
    tree.write(filename)


def main(level):
    links = []  # всі сайти для проходу
    links_mp3 = []  # всі посилання на mp3-файли
    data = []  # плейлист
    # Шукаємо вкладені сторінки із заданим рівнем (level)
    print "Parallel searching all deep links ..."
    gevent.joinall([gevent.spawn(get_links, lnk, level, links) for lnk in get_references()])

    # У знайдених сторінках шукаємо mp3-посилання
    print len(links), " links found" + '\nParallel searching mp3 links ...'
    gevent.joinall([gevent.spawn(search_mp3_links, lnk, links_mp3) for lnk in links])

    # Закачуємо файли за mp3-посиланнями
    print len(links_mp3), " mp3 links found" + "\nDownloading files ..."
    jobs = []
    i = 0
    for lnk in links_mp3:
        jobs.append(gevent.spawn(download_mp3, lnk, "song%d" % (i + 1)))
        i += 1
        if i == 5:
            break
    gevent.joinall(jobs)

    # Отримуємо інформацію із мета-даних
    # count = i
    i = 0
    jobs = []
    while i < 5:  # count:
        jobs.append(gevent.spawn(get_mp3_info, "mp3s//song%d.mp3" % (i + 1)))
        i += 1
    gevent.joinall(jobs)

    # Записуємо дані в плейлист
    write_xml(data)
    print "xml written successfully"


if __name__ == '__main__':
    time_st = time.time()
    main(0)
    time_end = time.time()
    print "time taken ", time_end - time_st
