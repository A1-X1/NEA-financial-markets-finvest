import unittest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os

# add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.pages.components.visualisation import GBMVisualisation

class TestVisualisationLimit(unittest.TestCase):
    def test_path_limiting_logic(self):
        # build test data with 5000 paths
        num_sims = 5000
        num_steps = 10
        data = np.random.randn(num_steps, num_sims)
        df = pd.DataFrame(data, columns=[str(i) for i in range(num_sims)])
        df['Mean'] = df.mean(axis=1)
        
        # calculate expected high and low from ALL 5000 paths
        expected_high = df[[str(i) for i in range(num_sims)]].max(axis=1)
        expected_low = df[[str(i) for i in range(num_sims)]].min(axis=1)

        # initialise visualisation
        viz = GBMVisualisation(
            title_input="Test Chart",
            data_input=df,
            currency_input="USD"
        )
        
        # generate chart
        fig = viz.generate_chart()
        
        # check number of traces
        # 3000 background paths + 1 high + 1 low + 1 mean = 3003 traces
        traces = fig.data
        # background paths are named 'Path {col}' but 'Mean Path' also has 'Path'
        background_paths = [t for t in traces if t.name and 'Path' in t.name and 'Mean' not in t.name]
        high_trace = next(t for t in traces if t.name == 'Daily High')
        low_trace = next(t for t in traces if t.name == 'Daily Low')
        mean_trace = next(t for t in traces if t.name == 'Mean Path')
        
        # verify trace counts
        self.assertEqual(len(background_paths), 3000, "Should only draw 3000 background paths")
        self.assertEqual(len(traces), 3003, "Total traces should be 3003")
        
        # verify bounds are based on 5000 paths, not 3000
        # check high trace against expected high of full dataset
        np.testing.assert_array_almost_equal(high_trace.y, expected_high, decimal=5)
        np.testing.assert_array_almost_equal(low_trace.y, expected_low, decimal=5)
        np.testing.assert_array_almost_equal(mean_trace.y, df['Mean'], decimal=5)
        
        print("Verification successful: Trace limit and calculation integrity confirmed.")

if __name__ == '__main__':
    unittest.main()
