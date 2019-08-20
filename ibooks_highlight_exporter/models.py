from typing import Type, TypeVar, List

import sys
import sqlite3

from ibooks_highlight_exporter import epub, helpers
from ibooks_highlight_exporter.base import TextPointer

B = TypeVar("B", bound="Book")
A = TypeVar("A", bound="Annotation")


class Book:
    def __init__(self, title: str, author: str, asset_id: str, epub_path: str):
        self.title = title
        self.author = author
        self.asset_id = asset_id
        self.epub_path = epub_path

    def __repr__(self):
        return f"{self.title} by {self.author}"

    @classmethod
    def get_all(cls: Type[B]) -> List[B]:
        database_path = helpers.get_ibooks_assets_database_path()

        if database_path is None:
            sys.exit("No iBooks library found.")

        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        books = []

        select_query = """
        select ZTITLE, ZAUTHOR, ZASSETID, ZPATH
        from ZBKLIBRARYASSET
        where ZPATH is not null
        order by ZASSETDETAILSMODIFICATIONDATE desc
        """

        for row in cursor.execute(select_query):

            import os

            epub_path = row[3]
            epub_content_path = epub.get_epub_content_path(epub_path)
            epub_toc_path = epub.get_epub_toc_path(epub_path)

            if epub_content_path is None and epub_toc_path is None:
                # try old format
                old_format_epub_path = os.path.join(row[3], "OEBPS")
                try:
                    epub_content_path = epub.get_epub_content_path(old_format_epub_path)
                    epub_toc_path = epub.get_epub_toc_path(old_format_epub_path)
                    epub_path = old_format_epub_path
                except FileNotFoundError:
                    pass

            if epub_content_path and epub_toc_path is not None:
                books.append(Book(row[0], row[1], row[2], epub_path))
        return books


class Annotation(TextPointer):
    def __init__(self, text_part, position, text, note=None):
        self.note = note
        super().__init__(text_part, position, text)

    def __repr__(self):
        return f"{self.text[:50]} from {self.text_part} at {self.position}"

    @classmethod
    def get_book_annotations(cls, book: Book) -> List[A]:
        database_path = helpers.get_ibooks_annotations_database_path()

        if database_path is None:
            sys.exit("No iBooks annotations found.")

        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        annotations = []

        select_query = f"""
        select ZANNOTATIONSELECTEDTEXT, ZANNOTATIONLOCATION, ZANNOTATIONNOTE
        from ZAEANNOTATION
        where ZANNOTATIONASSETID = '{book.asset_id}' and ZANNOTATIONSELECTEDTEXT is not null
        ORDER BY Z_PK
        """

        parts = epub.get_parts(book.epub_path)

        for row in cursor.execute(select_query):
            try:
                page_id, position = epub.parse_epub_cfi(row[1])
            except ValueError:
                continue
            annotations.append(
                Annotation(text=row[0], text_part=parts[page_id], position=position, note=row[2])
            )
        return annotations
