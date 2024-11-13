from refree import op
from refree.pattern import Pattern


def test_basic_pattern():
    pattern = op.begin + "test" + (op.digit * 3) + "end" + op.end
    assert str(pattern) == "^test(?:\\d{3})end$"


def test_email_pattern():
    pattern = op.seq(
        op.some(op.chars("a-zA-Z0-9._%+-")),  # username part
        "@",
        op.some(op.chars("a-zA-Z0-9.-")),  # domain part
        ".",
        op.between(2)(op.chars("a-zA-Z")),  # top-level domain
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


def test_complex_patterns():
    # Test combining multiple features
    date_pattern = op.seq(
        (op.digit * 4).named("year"),
        "-",
        (op.digit * 2).named("month"),
        "-",
        (op.digit * 2).named("day"),
    )
    assert date_pattern.match("2024-03-21")

    # Test alternation
    time_pattern = op.seq(
        op.chars("0-1") + op.digit | "2" + op.chars("0-3"),
        ":",
        op.chars("0-5") + op.digit,
    )

    assert time_pattern.match("23:59")
    assert time_pattern.match("08:30")
    assert not time_pattern.match("25:00")


def test_quantifiers():
    # Test various quantifiers
    pattern = op.seq(
        op.maybe("https"),  # optional https
        "://",
        op.some(op.word),  # domain
        op.many(op.seq("/", op.some(op.word))),  # optional paths
    )

    assert pattern.match("http://example.com")
    assert pattern.match("https://example.com/path/to/resource")
    assert not pattern.match("just_text")


def test_named_groups():
    # 使用 pattern.named() 方法
    pattern = op.seq(
        op.alt("http", "https").named("protocol"),
        "://",
        op.some(op.word).named("domain"),
    )

    match = pattern.match("https://example.com")
    assert match.group("protocol") == "https"
    assert match.group("domain") == "example.com"


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
    pattern = (op.digit * 4).named("year") + "-" + (op.digit * 2).named("month")

    assert pattern.groups == 2
    assert "year" in pattern.groupindex
    assert "month" in pattern.groupindex
