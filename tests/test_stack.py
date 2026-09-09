import sys
import os

# add project root to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.pages.components.stack import Stack

def test_stack_basic_operations():
    s = Stack()
    s.push(1)
    s.push(2)
    assert s.pop() == 2
    assert s.pop() == 1
    assert s.is_empty()
    print("test_stack_basic_operations passed")

def test_stack_max_size():
    # test that stack limits size to 5
    s = Stack(max_size=5)
    for i in range(10):
        s.push(i)
    
    assert s.size == 5
    # top should be 9
    assert s.pop() == 9
    assert s.pop() == 8
    assert s.pop() == 7
    assert s.pop() == 6
    assert s.pop() == 5
    assert s.is_empty()
    print("test_stack_max_size passed")

def test_stack_serialisation():
    s = Stack(max_size=5)
    s.push({'a': 1})
    s.push({'b': 2})
    
    lst = s.to_list()
    assert lst == [{'b': 2}, {'a': 1}]
    
    s2 = Stack(max_size=5)
    s2.from_list(lst)
    assert s2.pop() == {'b': 2}
    assert s2.pop() == {'a': 1}
    assert s2.is_empty()
    print("test_stack_serialisation passed")

if __name__ == "__main__":
    test_stack_basic_operations()
    test_stack_max_size()
    test_stack_serialisation()
    print("All Stack tests passed!")
