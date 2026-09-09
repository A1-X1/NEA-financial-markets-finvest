import sys
import os

# add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.pages.components.widgetLinkedList import WidgetLinkedList, WidgetNode

def test_linked_list_operations():
    ll = WidgetLinkedList()
    
    # test append
    node1 = WidgetNode('TypeA', {'k': 1})
    node2 = WidgetNode('TypeB', {'k': 2})
    node3 = WidgetNode('TypeC', {'k': 3})
    
    ll.append(node1)
    ll.append(node2)
    ll.append(node3)
    
    assert ll.size == 3
    assert ll.head.widget_id == node1.widget_id
    
    # test move down
    # state: [A, B, C] -> move A down -> [B, A, C]
    ll.move_down(node1.widget_id)
    assert ll.head.widget_id == node2.widget_id
    assert ll.head.next.widget_id == node1.widget_id
    
    # test move up
    # state: [B, A, C] -> move C up -> [B, C, A]
    ll.move_up(node3.widget_id)
    assert ll.head.next.widget_id == node3.widget_id
    
    # test remove
    ll.remove(node2.widget_id)
    assert ll.head.widget_id == node3.widget_id
    assert ll.size == 2
    
    # test serialisation
    data = ll.to_list()
    assert len(data) == 2
    assert data[0]['widget_type'] == 'TypeC'
    
    print("All linked list tests passed!")

if __name__ == "__main__":
    test_linked_list_operations()
