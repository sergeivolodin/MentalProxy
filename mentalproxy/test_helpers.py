
from mentalproxy.helpers import remove_cookie_word, WithGlobals
import pytest


def test_case_insensitive_pop_cookie():
    s = 'att=1-NEwhw1bS29wclktyN2TTVWojv7WcViuFVxcZMuwN; Max-Age=86400; Expires=Fri, 27 Jan 2023 15:25:22 GMT; Path=/; Domain=.twitter.com; Secure; HTTPOnly; Secure, SameSite=None'
    s = remove_cookie_word(s, 'secure')
    s = remove_cookie_word(s, 'domain')

    assert s == 'att=1-NEwhw1bS29wclktyN2TTVWojv7WcViuFVxcZMuwN; Max-Age=86400; Expires=Fri, 27 Jan 2023 15:25:22 GMT; Path=/; HTTPOnly; SameSite=None'
    
    
class MyClass(WithGlobals):
    @property
    def myproperty(self):
        raise NotImplementedError
    
def test_myclass_no_myproperty():
    with pytest.raises(NotImplementedError):
        MyClass().myproperty
        
def test_myclass_myproperty_set_withattr():
    cls1 = MyClass.setGlobal(myproperty=123)
    obj = cls1()
    assert obj.myproperty == 123
    
    assert cls1.__name__ != MyClass.__name__
    assert cls1.withGlobalsListGlobals() == {'myproperty': 123}

def test_myclass_different_names():
    cls1 = MyClass.setGlobal(myproperty=123)
    cls2 = MyClass.setGlobal(myproperty=456)
    
    assert cls1().myproperty == 123
    assert cls2().myproperty == 456
    
    assert cls1.__name__ != cls2.__name__