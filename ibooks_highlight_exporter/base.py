from functools import total_ordering


@total_ordering
class TextPointer:
    def __init__(self, text_part, position, text):
        self.text_part = text_part
        self.position = position
        self.text = text

    def __le__(self, other):
        if self.text_part != other.text_part:
            raise NotImplementedError(
                "Unable to compare pointers from different parts!"
            )
        return self.position < other.position


class HeadingPointer(TextPointer):
    def __init__(self, text_part, position, text, heading_level):
        self.heading_level = heading_level
        super().__init__(text_part, position, text)

    def __repr__(self):
        return f"h{self.heading_level} {self.text} at {self.text_part}#{self.position}"
