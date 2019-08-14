import click

from ibooks_highlight_exporter import exporter


@click.command()
def export():
    print("Which book do you want to export your highlights from?")
    books = exporter.get_books_available_for_export()
    for index, book in enumerate(books):
        print(f"{index + 1}. {book}")
    book_index = None
    while book_index is None:
        book_index_input = input("-> ")
        try:
            book_index = int(book_index_input)
        except ValueError:
            print("Invalid input, try again!")
        try:
            book = books[book_index - 1]
            print(f"Exporting highlights from {book}...")
        except IndexError:
            print(f"Invalid, try again with any number between 1 and {len(books)}!")
            book_index = None
        else:
            exporter.export(book)


if __name__ == "__main__":
    export()
