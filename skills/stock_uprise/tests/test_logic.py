
import sys
import os
import unittest

# Add parent dir to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from scanner import StockAnalyzer

class MockClient:
    pass

class TestStockUprise(unittest.TestCase):
    def setUp(self):
        self.client = MockClient()
        self.analyzer = StockAnalyzer(self.client)

    def test_volume_spike(self):
        # 100 avg volume
        history = [{'volume': 100}] * 21
        
        # Case 1: 150 volume (150%) -> False
        stock_info = {'volume': 150}
        self.assertFalse(self.analyzer.check_volume_spike(stock_info, history))
        
        # Case 2: 200 volume (200%) -> True
        stock_info = {'volume': 200}
        self.assertTrue(self.analyzer.check_volume_spike(stock_info, history))
        
        # Case 3: 300 volume (300%) -> True
        stock_info = {'volume': 300}
        self.assertTrue(self.analyzer.check_volume_spike(stock_info, history))

    def test_safe_zone(self):
        # Range 1000 to 2000. 30% level is 1300.
        history = [
            {'close': 1000}, # Min
            {'close': 2000}, # Max
            {'close': 1500} 
        ]
        
        # Case 1: 1200 (Safe)
        stock_info = {'price': 1200}
        self.assertTrue(self.analyzer.check_safe_zone(stock_info, history))
        
        # Case 2: 1300 (Boundary Safe)
        stock_info = {'price': 1300}
        self.assertTrue(self.analyzer.check_safe_zone(stock_info, history))
        
        # Case 3: 1301 (Unsafe)
        stock_info = {'price': 1301}
        self.assertFalse(self.analyzer.check_safe_zone(stock_info, history))

    def test_financial_health(self):
        # Case 1: All Good
        fund = {'operating_income': 100, 'PER': 10, 'PBR': 1, 'ROE': 5}
        self.assertTrue(self.analyzer.check_financial_health(fund))
        
        # Case 2: Negative Op Income
        fund = {'operating_income': -10, 'PER': 10, 'PBR': 1, 'ROE': 5}
        self.assertFalse(self.analyzer.check_financial_health(fund))
        
        # Case 3: Negative ROE
        fund = {'operating_income': 100, 'PER': 10, 'PBR': 1, 'ROE': -5}
        self.assertFalse(self.analyzer.check_financial_health(fund))
        
        # Case 4: Missing data (None) -> Strict mode returns False
        fund = {}
        self.assertFalse(self.analyzer.check_financial_health(fund))

    def test_pullback_resistance_breakout(self):
        # Extend history to pass len >= 10 check
        # Add 10 dummy days at beginning
        dummy = [{'high': 100, 'close': 90}] * 10
        
        recent = [
            {'high': 100, 'close': 90}, 
            {'high': 105, 'close': 95}, # Day -6 (Max High Logic target?)
            {'high': 100, 'close': 90},
            {'high': 100, 'close': 90},
            {'high': 100, 'close': 90},
            {'high': 100, 'close': 90},
            {'high': 100, 'close': 90}, # Day -1 (Max high 105 in window?)
            {'high': 110, 'close': 106} # Today (Close 106)
        ]
        
        history = dummy + recent
        
        # Logic: recent_6 = history[-7:-1]
        # In `recent` list:
        # Index -1 is Today.
        # -7:-1 are the 6 days prior. 
        # The list `recent` has 9 items.
        # recent[-7] is `{'high': 100, 'close': 90}` (3rd item)
        # Wait, let's trace carefully.
        # recent = [A, B(105), C, D, E, F, G(Day-1), H(Today)]
        # Slice -7:-1:
        # H is -1. G is -2. F is -3. E is -4. D is -5. C is -6. B is -7.
        # So slice includes B(105).
        # Max high in slice is 105.
        # Today close is 106.
        # 106 > 105 -> True.
        
        self.assertTrue(self.analyzer.check_pullback(history))
        
        # Case Fail
        history[-1]['close'] = 104
        self.assertFalse(self.analyzer.check_pullback(history))

if __name__ == '__main__':
    unittest.main()
