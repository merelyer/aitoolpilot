import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.content_engine import ContentEngine, GroqRateLimited

ROOT = Path(__file__).resolve().parents[1]


class GroqMigrationTests(unittest.TestCase):
    def test_client_uses_only_groq_secret_and_endpoint(self):
        with tempfile.TemporaryDirectory() as folder, patch('src.content_engine.ROOT', Path(folder)), patch.dict(os.environ, {'GROQ_API_KEY': 'test-only', 'DEEPSEEK_API_KEY': 'unused'}, clear=True), patch('src.content_engine.OpenAI') as client:
            ContentEngine(ROOT / 'config/settings.json')
        self.assertEqual(client.call_args.kwargs['api_key'], 'test-only')
        self.assertEqual(client.call_args.kwargs['base_url'], 'https://api.groq.com/openai/v1')

    def engine(self):
        engine = ContentEngine.__new__(ContentEngine)
        engine.model = 'openai/gpt-oss-120b'
        engine.client = Mock()
        engine.config = {'site': {'posts_per_run': 1, 'max_posts_per_run': 5}, 'seo': {'categories': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']}}
        engine._call_api = Mock(return_value='OK')
        engine.research_topics = Mock(return_value=[{'title': 'Topic'}])
        engine.generate_post = Mock(return_value={'title': 'Article'})
        engine.save_post = Mock()
        engine.build_site = Mock(return_value='site')
        return engine

    @patch('src.content_engine.time.sleep')
    def test_five_post_limit_applies_across_all_categories(self, sleep):
        engine = self.engine()
        self.assertEqual(len(engine.run_auto()), 5)
        self.assertEqual(engine.generate_post.call_count, 5)
        self.assertEqual(engine.research_topics.call_count, 5)

    def test_invalid_json_is_not_replaced_with_template(self):
        engine = self.engine()
        del engine.generate_post
        engine.site_name = 'Test'
        engine.max_tokens = 4000
        engine._call_api.return_value = '{bad json}'
        engine._fallback_post = Mock()
        self.assertIsNone(engine.generate_post({'title': 'Test'}, 'a'))
        engine._fallback_post.assert_not_called()

    def test_workflow_is_daily_and_uses_groq(self):
        text = (ROOT / '.github/workflows/auto-content.yml').read_text(encoding='utf-8')
        self.assertIn("cron: '15 1 * * *'", text)
        self.assertIn('secrets.GROQ_API_KEY', text)
        self.assertNotIn('DEEPSEEK_API_KEY', text)

    def test_quota_exhaustion_before_generation_skips_without_writes(self):
        engine = self.engine()
        engine._call_api.side_effect = GroqRateLimited('Quota reached')
        self.assertEqual(engine.run_auto(), [])
        engine.research_topics.assert_not_called()
        engine.save_post.assert_not_called()

    def test_quota_exhaustion_during_generation_stops_remaining_requests(self):
        engine = self.engine()
        engine.generate_post.side_effect = GroqRateLimited('Quota reached')
        self.assertEqual(engine.run_auto(), [])
        self.assertEqual(engine.research_topics.call_count, 1)
        engine.save_post.assert_not_called()

    def test_api_error_does_not_echo_provider_secret(self):
        engine = self.engine()
        del engine._call_api
        engine.max_tokens = 5000
        engine.temperature = 0.7
        error = RuntimeError('provider secret-value')
        error.status_code = 401
        engine.client.chat.completions.create.side_effect = error
        with self.assertRaisesRegex(RuntimeError, 'HTTP 401') as caught:
            engine._call_api('system', 'user')
        self.assertNotIn('secret-value', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
