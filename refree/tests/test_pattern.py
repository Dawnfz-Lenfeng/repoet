from refree import op
from refree.pattern import Pattern


def test_basic_pattern():
    pattern = op.begin + "test" + (op.digit * 3) + "end" + op.end
    assert str(pattern) == "^test(?:\\d{3})end$"


def test_email_pattern():
    pattern = op.seq(
        op.some(op.within("a-zA-Z0-9._%+-")),  # username part
        "@",
        op.some(op.within("a-zA-Z0-9.-")),  # domain part
        op.lit("."),
        op.between(2)(op.within("a-zA-Z")),  # top-level domain
    )

    # Test actual email addresses using Pattern methods directly
    assert pattern.match("test@example.com")
    assert pattern.match("user.name+tag@domain.com")
    assert not pattern.match("invalid@email")


def test_phone_pattern():
    pattern = op.begin + "1" + (op.digit * 10)
    assert str(pattern) == "^1(?:\\d{10})"

    # Test actual phone numbers using Pattern methods
    assert pattern.match("13812345678")
    assert not pattern.match("12345")


def test_quantifiers():
    # Test zero or one (maybe/optional) - matches 0-1 occurrence
    hex_color = op.seq(
        "#",
        op.maybe("0x"),  # optional hex prefix
        op.within("0-9A-Fa-f") * 6,  # exactly 6 hex digits
    )
    assert hex_color.match("#0xFFAABB")
    assert hex_color.match("#FF00CC")
    assert not hex_color.match("#12")  # too short

    # Test one or more (some) - matches 1+ occurrences
    number = op.seq(
        op.maybe("-"),
        op.some(op.digit),
        op.maybe(op.seq(".", op.some(op.digit))),
    )
    assert number.match("123")
    assert number.match("-42.5")
    assert number.match("0.123")
    assert not number.match(".")

    # Test zero or more (many) - matches 0+ occurrences
    comment = "/*" + op.many(op.any) + "*/"
    assert comment.match("/**/")
    assert comment.match("/* test comment */")
    assert not comment.match("/*")


def test_groups():
    # Test unnamed groups
    simple_pattern = op.seq(
        op.group(op.digit * 3),
        "-",
        op.group(op.digit * 4),
    )
    match = simple_pattern.match("123-4567")
    assert match.group(1) == "123"
    assert match.group(2) == "4567"

    # Test named groups
    date_pattern = op.seq(
        op.group(op.digit * 4, "year"),
        "-",
        op.group(op.digit * 2, "month"),
        "-",
        op.group(op.digit * 2, "day"),
    )
    match = date_pattern.match("2024-03-21")
    assert match.group("year") == "2024"
    assert match.group("month") == "03"
    assert match.group("day") == "21"

    # Test mixed named and unnamed groups
    url_pattern = op.seq(
        op.group(op.alt("http", "https"), "protocol"),
        "://",
        op.group(op.word),  # unnamed domain
        op.group("." + op.some(op.within("a-z")), "tld"),
    )
    match = url_pattern.match("https://example.com")
    assert match.group("protocol") == "https"
    assert match.group(2) == "example"
    assert match.group("tld") == ".com"

    # Test group properties
    assert url_pattern.groups == 3
    assert set(url_pattern.groupindex.keys()) == {"protocol", "tld"}


def test_pattern_methods():
    # Test additional Pattern methods
    pattern = op.seq(op.word, op.space, op.digit)

    # Test search
    assert pattern.search("prefix abc 5 suffix").group() == "abc 5"

    # Test findall
    results = pattern.findall("word 1 text 2")
    assert len(results) == 2

    # Test split
    comma_pattern = Pattern(",")
    assert comma_pattern.split("a,b,c") == ["a", "b", "c"]

    # Test substitution
    number_pattern = op.seq(op.digit * 3, "-", op.digit * 4)
    result = number_pattern.sub("XXX-XXXX", "Call 123-4567 or 890-1234")
    assert result == "Call XXX-XXXX or XXX-XXXX"


def test_pattern_properties():
    pattern = (
        op.group(op.digit * 4, name="year") + "-" + op.group(op.digit * 2, name="month")
    )

    assert pattern.groups == 2
    assert "year" in pattern.groupindex
    assert "month" in pattern.groupindex
