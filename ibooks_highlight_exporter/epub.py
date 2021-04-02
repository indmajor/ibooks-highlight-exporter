import os
import re
from collections import OrderedDict

from lxml import etree

from ibooks_highlight_exporter.helpers import find_first_file_with_extension
from ibooks_highlight_exporter.base import HeadingPointer


def get_epub_content_path(epub_directory_path: str) -> str:
    return find_first_file_with_extension(epub_directory_path, "opf")


def get_epub_toc_path(epub_directory_path: str) -> str:
    return find_first_file_with_extension(epub_directory_path, "ncx")


def get_parts(epub_directory_path: str) -> OrderedDict:
    opf = etree.parse(open(get_epub_content_path(epub_directory_path), "r"))
    parts = OrderedDict()
    for item in opf.xpath(
        "/*[local-name() = 'package']/*[local-name() = 'manifest']/*[local-name() = 'item']"
    ):
        if item.get("media-type") == "application/xhtml+xml":
            parts[item.get("id")] = item.get("href")
    return parts


def parse_epub_cfi(epub_cfi: str) -> (str, int):
    regex = re.compile(r"epubcfi\(/6/\d+\[(.+)\]!/4(.*?)/(\d+)")
    m = regex.search(epub_cfi)
    if m is None:
        raise ValueError("Invalid epubcfi!")
    else:
        part_id = m.group(1)
        try:
            position = int(m.group(3))
        except ValueError:
            raise ValueError("Invalid epubcfi!")
        return part_id, position


def get_heading_pointers(epub_path):
    toc_path = get_epub_toc_path(epub_path)
    toc = etree.parse(open(toc_path, "r"))

    first_level_nav_points = toc.xpath(
        "/*[local-name() = 'ncx']/*[local-name() = 'navMap']/*[local-name() = 'navPoint']"
    )

    chapter_links = []

    for nav_point in first_level_nav_points:
        chapter_links += traverse_nav_point(nav_point)

    return find_chapter_positions(chapter_links, epub_path)


def traverse_nav_point(nav_point, level=0):
    src = nav_point.xpath("./*[local-name() = 'content']")[0].get("src")

    if "#" in src:
        html_path, a_id = tuple(src.split("#"))
    else:
        html_path = src
        a_id = None

    chapter_name = nav_point.xpath(
        "./*[local-name() = 'navLabel']/*[local-name() = 'text']"
    )[0].text
    sub_nav_points = nav_point.xpath("./*[local-name() = 'navPoint']")

    chapter_links = [(html_path, chapter_name, a_id, level)]

    for sub_nav_point in sub_nav_points:
        chapter_links += traverse_nav_point(sub_nav_point, level + 1)
    return chapter_links


def find_chapter_positions(chapter_links, epub_path):
    heading_pointers = []

    for chapter_link in chapter_links:
        tree = etree.parse(open(os.path.join(epub_path, chapter_link[0]), "r"))
        body_xpath = "/*[local-name() = 'html'] /*[local-name() = 'body']"
        body = tree.xpath(body_xpath)[0]

        if chapter_link[2] is not None:
            el = body.xpath(f"//*[@id='{chapter_link[2]}']")[0]
            ancestor_before_body = el
            for ancestor in el.iterancestors():
                if ancestor.tag.endswith("body"):
                    break
                ancestor_before_body = ancestor

            position = body.index(ancestor_before_body) * 2
        else:
            position = 0
        heading_pointers.append(
            HeadingPointer(
                chapter_link[0], int(position), chapter_link[1], chapter_link[3]
            )
        )

    return heading_pointers
