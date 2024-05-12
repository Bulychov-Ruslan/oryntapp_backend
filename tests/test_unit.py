# Модульные тесты
import unittest
from main import format_parking_status

class TestFormatParkingStatus(unittest.TestCase):
    def test_format_parking_status(self):
        parking_config = {'layout': {'rows': [{'count': 2}, {'count': 3}]}}
        status = [True, False, True, True, False]
        expected_result = [[True, False], [True, True, False]]
        result = format_parking_status(parking_config, status)
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
