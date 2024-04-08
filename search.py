from transliterate import translit, detect_language
from fuzzywuzzy import fuzz

import loggers


def ratio(s1: str, s2: str) -> int:
    __ratio: int = fuzz.ratio(s1, s2)
    loggers.search.info(f'"{s1}" & "{s2}" -> {__ratio}')
    return __ratio


def translit_en(s: str) -> str:
    """
    Transliterate string to English.
    :param s: string to transliterate.
    :return: transliterated string.
    """
    return s if not detect_language(s) else translit(s, reversed=True)


def translit_uk(s: str) -> str:
    """
    Transliterate string to Ukrainian.
    :param s: string to transliterate.
    :return: transliterated string.
    """
    return translit(s, 'uk') if detect_language(s) != 'uk' else s


async def is_match(s1: str, s2: str, /, *, __ratio: float = 50) -> bool:
    """
    Matching algorithm to compare the product title in the database and prompted by the user title.
    :param s1:
    :param s2:
    :param __ratio: fuzzy search ratio.
    :return: True if s1 matches s2, False otherwise.
    """
    s1, s2 = s1.lower(), s2.lower()
    __is_match: bool = (
            ratio(s1, s2) >= __ratio
            or
            ratio(translit_en(s1), translit_en(s2)) >= __ratio
            or
            ratio(translit_uk(s1), translit_uk(s2)) >= __ratio
            or
            s1 in s2  # FIXME: review
            or
            s2 in s1  # FIXME: review
    )
    getattr(loggers.search, 'success' if __is_match else 'error')(f'"{s1}" & "{s2}" -> {__is_match}')
    return __is_match
