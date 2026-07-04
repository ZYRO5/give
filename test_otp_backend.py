import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

import server


class OtpBackendTests(unittest.TestCase):
    def test_normalize_phone_number_for_indian_mobile(self):
        self.assertEqual(server.normalize_phone_number('9876543210'), '+919876543210')

    def test_normalize_phone_number_keeps_international_format(self):
        self.assertEqual(server.normalize_phone_number('+447700900123'), '+447700900123')

    def test_payment_details_include_bank_account(self):
        details = server.get_payment_details(500)
        self.assertTrue(details['success'])
        self.assertEqual(details['bank_account']['account_number'], '42818590419')
        self.assertEqual(details['bank_account']['ifsc_code'], 'SBIN0021400')

    def test_payment_receipt_contains_transfer_instructions(self):
        receipt = server.build_payment_receipt(
            transaction_id='PAY-123',
            amount=1000,
            donor_name='Jane Doe',
            donor_email='jane@example.com',
            donor_phone='9876543210',
            donor_address='Hyderabad',
        )
        self.assertIn('PAY-123', receipt)
        self.assertIn('Payment UTR', receipt)
        self.assertNotIn('42818590419', receipt)
        self.assertNotIn('SBIN0021400', receipt)

    def test_delivery_error_message_mentions_unverified_number(self):
        message = server.build_delivery_error_message(RuntimeError('21608 The phone number is unverified. Trial accounts cannot send messages to unverified numbers.'))
        self.assertIn('verify the phone number', message.lower())
        self.assertIn('twilio', message.lower())

    def test_payment_window_defaults_to_fifteen_minutes(self):
        window = server.build_payment_window(15)
        self.assertEqual(window['expires_in_minutes'], 15)
        self.assertIn('expires_at', window)
        self.assertIn('payment_modes', window)
        self.assertIn('UPI', window['payment_modes'])


if __name__ == '__main__':
    unittest.main()
