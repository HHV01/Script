"""Keep channel identity in management data, out of audience-facing content."""
import re
import unicodedata

ALIASES = ('Dấu Vết Văn Minh', 'LsDấuVếtVănMinh')


def compact(text):
    value=unicodedata.normalize('NFKD',text).casefold().replace('đ','d')
    return ''.join(c for c in value if c.isalnum() and not unicodedata.combining(c))


def contains_brand(text):
    value=compact(text)
    return any(compact(name) in value for name in ALIASES)


def remove_branded_sentences(text):
    from .s1_script import split_sentences
    paragraphs=[]
    for paragraph in re.split(r'\n\s*\n',text.strip()):
        kept=[sentence for sentence in split_sentences(paragraph) if not contains_brand(sentence)]
        if kept:paragraphs.append(' '.join(kept))
    return '\n\n'.join(paragraphs)
