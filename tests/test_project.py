import unittest
from unittest.mock import patch
from engine import Agent
from bug_detective import evaluate, investigate, BUG, FIX
class Tests(unittest.TestCase):
    def test_reproduction(self): self.assertFalse(all(r['passed'] for r in evaluate(BUG)))
    def test_regression(self): self.assertTrue(all(r['passed'] for r in evaluate(FIX)))
    def test_disallowed_calls(self):
        with self.assertRaises(ValueError): evaluate("__import__('os').getcwd()")
    def test_bug_flow(self):
        a=Agent()
        self.assertEqual(investigate(a)['status'],'verified_on_bundled_cases')
        self.assertEqual(len(a.trace),2)
    def test_retry_bound(self):
        with patch.object(Agent,'run',return_value={'expression':BUG}): result=investigate(Agent())
        self.assertEqual(result['status'],'needs_review')
        self.assertEqual(len(result['attempts']),2)
    def test_missing_key(self):
        with patch.dict('os.environ',{},clear=True):
            with self.assertRaisesRegex(ValueError,'OPENAI_API_KEY'): Agent(True).run('role',{}, {})
