import unittest
from unittest.mock import Mock

from src.content_engine import ContentEngine


class GenerationPreflightTests(unittest.TestCase):
    def engine(self):
        engine = ContentEngine.__new__(ContentEngine)
        engine.model = 'deepseek-chat'
        engine.config = {'seo': {'categories': []}}
        engine.client = Mock()
        engine._call_api = Mock(return_value='OK')
        engine.build_site = Mock()
        engine.save_post = Mock()
        return engine

    def test_api_failure_stops_before_writing_content(self):
        engine = self.engine()
        engine._call_api.side_effect = RuntimeError('401 Authentication Fails secret-value')
        with self.assertRaisesRegex(RuntimeError, 'DEEPSEEK_API_KEY') as error:
            engine.run_auto()
        self.assertNotIn('secret-value', str(error.exception))
        engine.save_post.assert_not_called()
        engine.build_site.assert_not_called()

    def test_missing_client_stops_automated_generation(self):
        engine = self.engine()
        engine.client = None
        with self.assertRaisesRegex(RuntimeError, 'DEEPSEEK_API_KEY'):
            engine.run_auto()
        engine._call_api.assert_not_called()

    def test_valid_api_allows_generation(self):
        engine = self.engine()
        self.assertEqual(engine.run_auto(), [])
        engine._call_api.assert_called_once()

    def test_empty_api_response_stops_generation(self):
        engine = self.engine()
        engine._call_api.return_value = None
        with self.assertRaisesRegex(RuntimeError, 'DEEPSEEK_API_KEY'):
            engine.run_auto()
        engine.build_site.assert_not_called()


if __name__ == '__main__':
    unittest.main()
