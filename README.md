# RePoet: Write Regular Expressions Like Poetry in Python

[![PyPI version](https://badge.fury.io/py/repoet.svg)](https://badge.fury.io/py/repoet)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

🎯 Transform regex into poetry! Write regular expressions as elegantly as writing verses.

## ✨ Highlights

```python
from repoet import op

# Traditional regex (cryptic spell)
date_regex = r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})$"

# With RePoet (elegant verse)
date = op.seq(
    op.begin,
    op.group(op.digit * 4, name="year") + "-",
    op.group(op.digit * 2, name="month") + "-",
    op.group(op.digit * 2, name="day"),
    op.end
)

match = date.match("2024-03-01")
print(match.group("year"))   # "2024"
print(match.group("month"))  # "03"
print(match.group("day"))    # "01"
```

## 🚀 Why RePoet?

- **🎭 Full Re API Compatibility** - All `re` module features are supported
- **🎨 Operator Magic** - Use `+`, `|`, `*` to compose patterns naturally
- **📝 Multiple Styles** - Choose between operator style or functional style
- **🛡️ Type-Safe** - Full type hints for better IDE support
- **🎯 Zero Learning Curve** - If you know regex, you know RePoet

## 💫 Quick Start

```bash
pip install repoet
```

## 📖 Core Concepts

### Pattern Composition

```python
from repoet import op

# Using operators
pattern = op.digit + op.word + op.space    # \d\w+\s
pattern = op.digit | op.word               # (?:\d|\w+)
pattern = op.digit * 3                     # \d{3}

# Using functions
pattern = op.seq(op.digit, op.word, op.space)
pattern = op.alt(op.digit, op.word)
pattern = op.times(3)(op.digit)
```

### Named Groups & Captures

```python
# Match phone numbers with named groups
phone = op.seq(
    op.maybe("+"),
    op.group(op.digit * 2, "country"),
    " ",
    op.group(op.digit * 3, "area"),
    "-",
    op.group(op.digit * 4, "number")
)

match = phone.match("+86 123-4567")
print(match.group("country"))  # "86"
print(match.group("number"))   # "4567"
```

### Advanced Features

```python
# Lookarounds
price = op.behind("$") + op.digit * 2      # (?<=\$)\d{2}
not_end = op.word + op.not_ahead(op.end)   # \w+(?!$)

# Character Classes
username = op.some(op.anyof("a-zA-Z0-9_"))  # [a-zA-Z0-9_]+
not_digit = op.exclude("0-9")               # [^0-9]

# Quantifiers
optional = op.maybe("s")                    # s?
one_plus = op.some(op.letter)               # \w+
any_amount = op.mightsome(op.space)         # \s*
```

## 🎯 Pattern API

RePoet patterns support all standard `re` module methods:

```python
pattern = op.word + "@" + op.word

# All re module methods are available
pattern.match(string)
pattern.search(string)
pattern.findall(string)
pattern.finditer(string)
pattern.sub(repl, string)
pattern.split(string)
```

## 📚 More Examples

### URL Parser
```python
url = op.seq(
    op.group(op.alt("http", "https"), "protocol"),
    "://",
    op.group(op.some(op.anyof("a-z0-9.-")), "domain"),
    op.group(op.mightsome(op.anyof("/a-z0-9.-")), "path")
)
```

### Date Validator
```python
date = (op.digit * 4) + "-" + \
       (op.digit * 2) + "-" + \
       (op.digit * 2)
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

⭐️ If you find RePoet useful, please star it on GitHub! ⭐️
