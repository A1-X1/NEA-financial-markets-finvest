import sys
import os

# add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.pages.portfolio import PortfolioPage

def test_csv_parsing():
    # valid csv content matching the export format
    csv_content = b"Ticker,Quantity,Price,Currency,Value (Local)\nAAPL,10,150.00,USD,1500.00\nTSLA,5,200.00,USD,1000.00"
    
    parsed = PortfolioPage.parse_import_csv(csv_content)
    
    assert len(parsed) == 2
    assert parsed[0] == ('AAPL', 10.0)
    assert parsed[1] == ('TSLA', 5.0)
    
    # invalid csv content
    invalid_content = b"Wrong,Header\nData,10"
    try:
        PortfolioPage.parse_import_csv(invalid_content)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
        
    print("All CSV parsing tests passed!")

if __name__ == "__main__":
    test_csv_parsing()
