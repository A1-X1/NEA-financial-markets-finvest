import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import sys
import os

# add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.portfolio_sorter import calculate_sharpe_ratio, merge_sort_portfolios

class TestPortfolioSorter(unittest.TestCase):

    @patch('yfinance.download')
    def test_calculate_sharpe_ratio(self, mock_download):
        # mock historical data for two stocks
        dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
        mock_data = pd.DataFrame({
            'AAPL': [150 + i for i in range(10)], # upward trend (high sharpe)
            'GOOG': [100 - i for i in range(10)]  # downward trend (negative sharpe)
        }, index=dates)
        
        # mock download to return our df
        mock_download.return_value = MagicMock()
        mock_download.return_value.__getitem__.return_value = mock_data
        
        # portfolio 1: AAPL only
        sr_aapl = calculate_sharpe_ratio([('AAPL', 10)])
        # portfolio 2: GOOG only
        sr_goog = calculate_sharpe_ratio([('GOOG', 10)])
        
        self.assertGreater(sr_aapl, sr_goog, "AAPL (upward) should have higher Sharpe than GOOG (downward)")

    @patch('modules.portfolio_sorter.calculate_sharpe_ratio')
    def test_merge_sort_portfolios(self, mock_sr):
        # mock sharpe ratios for different portfolios
        # side_effect returns values in sequence
        mock_sr.side_effect = []
        
        portfolios = []
        
        # test descending sort (default)
        sorted_ports = merge_sort_portfolios(portfolios, descending=True)

        print(f'Descending sort: {sorted_ports}')
        
        # self.assertEqual(sorted_ports[0]['name'], 'Portfolio C')
        # self.assertEqual(sorted_ports[1]['name'], 'Portfolio B')
        # self.assertEqual(sorted_ports[2]['name'], 'Portfolio A')

        portfolios = [
            {'name': 'Portfolio A', 'items': [('T1', 10)]}, 
            {'name': 'Portfolio B', 'items': [('T2', 10)]}, 
            {'name': 'Portfolio C', 'items': [('T3', 10)]}  
        ]
        
        # test ascending sort
        mock_sr.side_effect = [1.5, 0.5, 2.0]
        sorted_ports_asc = merge_sort_portfolios(portfolios, descending=False)

        print(f'Ascending sort: {sorted_ports_asc}')
        
        self.assertEqual(sorted_ports_asc[0]['name'], 'Portfolio B')
        self.assertEqual(sorted_ports_asc[1]['name'], 'Portfolio A')
        self.assertEqual(sorted_ports_asc[2]['name'], 'Portfolio C')

if __name__ == '__main__':
    unittest.main()
