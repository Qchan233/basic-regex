from regex import re_parse
from regex import match

assert re_parse('') is None
assert re_parse('.') == 'dot'
assert re_parse('a') == 'a'
assert re_parse('ab') == ('cat', 'a', 'b')
assert re_parse('a|b') == ('split', 'a', 'b')
assert re_parse('a*') == ('repeat', 'a')
assert re_parse('a|bc') == ('split', 'a', ('cat', 'b', 'c'))

assert match('', '')
assert not match('', 'a')
assert match('a*', 'a')
assert match('a*', 'aaaa')
assert match('a|b', 'a')
assert match('a|b', 'b')
assert not match('a|b', 'c')
assert match('ab', 'ab')
assert not match('ab', 'ac')
assert match('ab|c', 'ab')
assert match('ab|c', 'c')
assert not match('ab|c', 'd')
assert match('a*b', 'b')
assert match('a*b', 'ab')
assert match('a*b', 'aaaaab')
assert match('a|b*', 'a')
assert match('a|b*', 'bb')
assert match('a|b*', 'bbb')
assert not match('a|b*', 'abbb')