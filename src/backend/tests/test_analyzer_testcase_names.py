import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analyzer import CodeAnalyzer


class AnalyzerTestcaseNamesTests(unittest.TestCase):
    def test_evaluate_testcases_includes_testcase_name(self):
        analyzer = CodeAnalyzer()
        testcase = {
            'input': '5\n',
            'expected_output': '5\n',
            'name': 'Sample case',
            'ten_testcase': 'Sample case'
        }

        with patch.object(analyzer, 'compile', return_value={'success': True, 'executable': 'fake.exe'}):
            with patch('analyzer.subprocess.run', return_value=SimpleNamespace(returncode=0, stdout='5\n', stderr='')):
                result = analyzer.evaluate_testcases('int main(){return 0;}', [testcase])

        self.assertEqual(result['test_results'][0]['name'], 'Sample case')
        self.assertEqual(result['test_results'][0]['testcase_name'], 'Sample case')


if __name__ == '__main__':
    unittest.main()
