from repoet import op
from repoet.pattern import Pattern


def test_basic_pattern():
    pattern = op.begin + "test" + (op.digit * 3) + "end" + op.end
    assert str(pattern) == "^test(?:\\d{3})end$"


def test_quantifiers():
    # Test zero or one (maybe/optional)
    hex_color = op.seq(
        "#",
        op.maybe("0x"),
        op.anyof("0-9A-Fa-f") * 6,
    )
    assert hex_color.match("#0xFFAABB")
    assert hex_color.match("#FF00CC")
    assert not hex_color.match("#12")

    # Test one or more (some)
    number = op.seq(
        op.maybe("-"),
        op.some(op.digit),
        op.maybe(op.seq(".", op.some(op.digit))),
    )
    assert number.match("123")
    assert number.match("-42.5")
    assert number.match("0.123")
    assert not number.match(".")

    # Test zero or more (mightsome)
    comment = "/*" + op.mightsome(op.any) + "*/"
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
        op.group(op.word),
        op.group("." + op.some(op.anyof("a-z")), "tld"),
    )
    match = url_pattern.match("https://example.com")
    assert match.group("protocol") == "https"
    assert match.group(2) == "example"
    assert match.group("tld") == ".com"

    # Test group properties
    assert url_pattern.groups == 3
    assert set(url_pattern.groupindex.keys()) == {"protocol", "tld"}


def test_pattern_methods():
    pattern = op.word + op.space + op.digit
    assert pattern.search("prefix abc 5 suffix").group() == "abc 5"

    results = pattern.findall("word 1 text 2")
    assert len(results) == 2

    comma_pattern = Pattern(",")
    assert comma_pattern.split("a,b,c") == ["a", "b", "c"]

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


def test_character_classes():
    """Test built-in character classes"""
    # Test basic character classes
    assert op.digit.match("5")
    assert not op.digit.match("a")
    assert op.letter.match("a")
    assert op.letter.match("5")
    assert op.letter.match("_")
    assert not op.letter.match("!")
    assert op.nonletter.match("!")
    assert not op.nonletter.match("a")

    # Test whitespace classes
    assert op.space.match(" ")
    assert op.space.match("\t")
    assert op.space.match("\n")
    assert not op.space.match("x")
    assert op.nonspace.match("x")
    assert not op.nonspace.match(" ")


def test_boundary_matchers():
    """Test word boundaries and line anchors"""
    # Word boundaries
    cat_pattern = op.bound + "cat" + op.bound
    assert cat_pattern.search("my cat sleeps")
    assert not cat_pattern.search("category")
    assert not cat_pattern.search("tomcat")

    # Line anchors - begin
    hello_pattern = op.begin + "Hello"
    assert hello_pattern.search("Hello world")
    assert not hello_pattern.search(" Hello")
    assert not hello_pattern.search("Say Hello")

    # Line anchors - end
    bye_pattern = "bye" + op.end
    assert bye_pattern.search("good bye")
    assert not bye_pattern.search("bye ")
    assert not bye_pattern.search("bye_")


def test_lookaround():
    """Test lookahead and lookbehind assertions"""
    # Positive lookahead
    dollars = op.digit + op.ahead("$")
    assert dollars.match("5$")
    assert not dollars.match("5€")

    # Negative lookahead
    no_vowel = op.some(op.exclude("aeiou")) + op.not_ahead(op.anyof("aeiou"))
    assert no_vowel.fullmatch("dry")
    assert not no_vowel.fullmatch("dye")

    # Positive lookbehind
    after_hash = op.behind("#") + op.word
    assert after_hash.search("#tag")
    assert not after_hash.search("@tag")

    # Negative lookbehind
    no_digit_before = op.not_behind(op.digit) + op.some(op.anyof("a-z"))
    assert no_digit_before.fullmatch("abc")
    assert not no_digit_before.fullmatch("1abc")


def test_greedy_vs_nongreedy():
    """Test greedy and non-greedy quantifiers"""
    text = "<tag>content</tag>"

    # Greedy matching
    greedy = op.seq("<", op.some(op.any), ">")
    assert greedy.search(text).group() == "<tag>content</tag>"

    # Non-greedy matching
    non_greedy = op.seq("<", op.some(op.any, greedy=False), ">")
    assert non_greedy.search(text).group() == "<tag>"


def test_between_quantifier():
    """Test the between quantifier with different ranges"""
    # Exact count
    three_digits = op.between(3, 3)(op.digit)
    assert three_digits.match("123")
    assert not three_digits.match("12")
    assert not three_digits.fullmatch("1234")

    # Range with upper bound
    phone = op.between(2, 4)(op.digit)
    assert phone.match("12")
    assert phone.match("123")
    assert phone.match("1234")
    assert not phone.fullmatch("12345")

    # Range without upper bound
    many_digits = op.between(2, None)(op.digit)
    assert many_digits.match("12")
    assert many_digits.match("123456789")


def test_pattern_composition():
    """Test complex pattern composition"""
    # Email pattern
    email = op.seq(
        op.some(op.anyof(op.letter + "._")),  # username
        "@",
        op.some(op.some(op.anyof("a-z")) + op.anyof("._")),  # domain
        op.between(2, 4)(op.letter),  # TLD
    )

    assert email.match("user@example.com")
    assert email.match("user.name@sub_domain.co.uk")
    assert not email.match("invalid@email")
    assert not email.match("@domain.com")


def test_special_characters():
    """Test handling of special regex characters"""
    # Test literal dots
    dot_pattern = op.lit(".") + op.digit
    assert dot_pattern.match(".5")
    assert not dot_pattern.match("x5")

    # Test escaping in character classes
    special_chars = op.anyof(".*+?[](){}^$|\-\\")
    assert all(special_chars.match(c) for c in ".*+?[](){}^$|-\\")
