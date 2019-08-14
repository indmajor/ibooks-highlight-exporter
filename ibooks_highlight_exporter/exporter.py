from collections import OrderedDict
from typing import List
from xml.etree import ElementTree as ET

from ibooks_highlight_exporter import epub, models, base


def get_books_available_for_export() -> List[models.Book]:
    return models.Book.get_all()


def export(book: models.Book):
    annotations = models.Annotation.get_book_annotations(book)
    heading_pointers = epub.get_heading_pointers(book.epub_path)

    sorted_parts = list(OrderedDict.fromkeys([h.text_part for h in heading_pointers]))

    html = ET.Element("html")
    body = ET.Element("body")
    html.append(body)

    for part in sorted_parts:
        part_headings = list(filter(lambda h: h.text_part == part, heading_pointers))
        part_annotations = list(filter(lambda a: a.text_part == part, annotations))

        if part_annotations:
            part_texts = sorted(part_headings + part_annotations)
            for text in part_texts:
                tag = "p"
                if isinstance(text, base.HeadingPointer):
                    tag = f"h{text.heading_level + 1}"
                el = ET.Element(tag)
                el.text = text.text
                body.append(el)

    ET.ElementTree(html).write(f"{book.title}_highlights.html")
