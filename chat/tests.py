import os
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from .agent import run_agent
from .models import Item
from .tools import add_item, check_stock, remove_stock, set_price


class InventoryTests(TestCase):
    def test_create_restock_and_price(self):
        self.assertTrue(add_item('Hammer', 3, 12.50)['created'])
        self.assertFalse(add_item('hammer', 2)['created'])
        self.assertEqual(check_stock('HAMMER')['quantity'], 5)
        set_price('Hammer', 15)
        self.assertEqual(check_stock('Hammer')['price'], 15)

    def test_insufficient_stock_does_not_change_database(self):
        add_item('Hammer', 3)
        self.assertIn('error', remove_stock('Hammer', 4))
        self.assertEqual(Item.objects.get(name='Hammer').quantity, 3)

    def test_home_loads_without_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertContains(self.client.get('/'), 'Inventory Agent')

    @patch('chat.views.run_agent', return_value=('There are 3 hammers.', 'interaction-1'))
    def test_chat_stores_answer_and_conversation_id(self, agent):
        response = self.client.post('/', {'message': 'How many hammers?'})
        self.assertRedirects(response, '/')
        agent.assert_called_once_with('How many hammers?', None)
        self.assertEqual(self.client.session['interaction_id'], 'interaction-1')
        self.assertEqual(self.client.session['history'][-1]['text'], 'There are 3 hammers.')

    @patch('chat.views.run_agent')
    def test_empty_message_does_not_call_gemini(self, agent):
        self.client.post('/', {'message': '   '})
        agent.assert_not_called()

    def test_missing_key_is_reported_without_network_call(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'GEMINI_API_KEY'):
                run_agent('Hello')

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-only'})
    @patch('chat.agent.genai.Client')
    def test_agent_executes_inventory_tool(self, client_factory):
        add_item('Hammer', 3, 12.5)
        create = client_factory.return_value.interactions.create
        create.side_effect = [
            SimpleNamespace(id='first', steps=[SimpleNamespace(
                type='function_call', name='check_stock',
                arguments={'name': 'Hammer'}, id='call-1',
            )]),
            SimpleNamespace(id='second', steps=[], output_text='3 hammers.'),
        ]
        self.assertEqual(run_agent('How many hammers?'), ('3 hammers.', 'second'))
        payload = create.call_args.kwargs['input'][0]
        self.assertEqual(payload['call_id'], 'call-1')
        self.assertIn('"quantity": 3', payload['result'][0]['text'])

    def test_reset_clears_history(self):
        session = self.client.session
        session['history'] = [{'role': 'user', 'text': 'hello'}]
        session.save()
        self.client.get('/reset/')
        self.assertNotIn('history', self.client.session)
