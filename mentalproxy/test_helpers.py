
from mentalproxy.helpers import remove_cookie_word


def test_case_insensitive_pop_cookie():
    s = 'att=1-NEwhw1bS29wclktyN2TTVWojv7WcViuFVxcZMuwN; Max-Age=86400; Expires=Fri, 27 Jan 2023 15:25:22 GMT; Path=/; Domain=.twitter.com; Secure; HTTPOnly; Secure, SameSite=None'
    s = remove_cookie_word(s, 'secure')
    s = remove_cookie_word(s, 'domain')

    assert s == 'att=1-NEwhw1bS29wclktyN2TTVWojv7WcViuFVxcZMuwN; Max-Age=86400; Expires=Fri, 27 Jan 2023 15:25:22 GMT; Path=/; HTTPOnly; SameSite=None'