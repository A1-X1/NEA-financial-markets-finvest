import sys
import os

# add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.pages.components.hashTable import HashTable

def test_duplicate_key_addition():
    # setup hash table
    ht = HashTable()
    
    # test adding initial value
    ticker = "TSLA"
    ht.put(ticker, 100.0)
    print(f"Initial {ticker}: {ht.get(ticker)}")
    
    # test adding duplicate key
    ht.put(ticker, 50.0)
    print(f"After adding 50 {ticker}: {ht.get(ticker)}")
    
    # verify the total quantity
    result = ht.get(ticker)
    expected = 150.0
    
    print(f"Testing {ticker} addition")
    print(f"Actual: {result}, Expected: {expected}")
    
    if result == expected:
        print("Test passed: duplicate key increments quantity")
        return True
    
    print("Test failed")
    return False

if __name__ == "__main__":
    if test_duplicate_key_addition():
        sys.exit(0)
    else:
        sys.exit(1)
