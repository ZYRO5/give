import React from 'react';
import { Button, Card } from './UI';
import { Download, Check } from 'lucide-react';

interface PaymentModalProps {
  isOpen: boolean;
  amount: number;
  campaignTitle: string;
  onClose: () => void;
  onPaymentSuccess: () => void;
}

declare global {
  interface Window {
    Razorpay: any;
  }
}

const PaymentModal: React.FC<PaymentModalProps> = ({
  isOpen,
  amount,
  campaignTitle,
  onClose,
  onPaymentSuccess,
}) => {
  const [loading, setLoading] = React.useState(false);
  const [paymentMethod, setPaymentMethod] = React.useState<'razorpay' | 'bank_transfer'>('razorpay');
  const [bankDetails, setBankDetails] = React.useState<any>(null);

  React.useEffect(() => {
    if (isOpen) {
      fetchBankDetails();
      loadRazorpayScript();
    }
  }, [isOpen]);

  const fetchBankDetails = async () => {
    try {
      const response = await fetch('/api/v1/payments/bank-details');
      const data = await response.json();
      setBankDetails(data);
    } catch (error) {
      console.error('Error fetching bank details:', error);
    }
  };

  const loadRazorpayScript = () => {
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    document.body.appendChild(script);
  };

  const handleRazorpayPayment = async () => {
    setLoading(true);
    try {
      // Initiate payment
      const response = await fetch('/api/v1/payments/initiate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount,
          donor_name: 'Donor Name', // Get from context
          donor_email: 'donor@example.com', // Get from context
          campaign_id: 'campaign-id',
          donor_id: 'donor-id',
        }),
      });

      const paymentData = await response.json();

      const options = {
        key: paymentData.key_id,
        amount: paymentData.amount * 100,
        currency: paymentData.currency,
        name: paymentData.recipient_name,
        description: campaignTitle,
        order_id: paymentData.order_id,
        handler: (response: any) => {
          verifyPayment(response);
        },
        theme: {
          color: '#3b82f6',
        },
      };

      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (error) {
      console.error('Error initiating payment:', error);
      alert('Failed to initiate payment');
    } finally {
      setLoading(false);
    }
  };

  const verifyPayment = async (razorpayResponse: any) => {
    try {
      const response = await fetch('/api/v1/payments/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          razorpay_order_id: razorpayResponse.razorpay_order_id,
          razorpay_payment_id: razorpayResponse.razorpay_payment_id,
          razorpay_signature: razorpayResponse.razorpay_signature,
        }),
      });

      if (response.ok) {
        alert('Payment successful!');
        onPaymentSuccess();
        onClose();
      } else {
        alert('Payment verification failed');
      }
    } catch (error) {
      console.error('Error verifying payment:', error);
      alert('Error verifying payment');
    }
  };

  const downloadBankTransferReceipt = () => {
    const bankInfo = bankDetails?.bank_account;
    const receiptContent = `
BANK TRANSFER DETAILS
====================

Campaign: ${campaignTitle}
Amount: ₹${amount}

Recipient Details:
Name: ${bankDetails?.recipient_name}
Email: ${bankDetails?.recipient_email}

Bank Account:
Account Holder: ${bankInfo?.account_holder_name}
Account Number: ${bankInfo?.account_number}
Account Type: ${bankInfo?.account_type}
IFSC Code: ${bankInfo?.ifsc_code}
Bank Branch: ${bankInfo?.bank_branch}

Please transfer the above amount and send proof to:
${bankDetails?.recipient_email}

Thank you for your donation!
    `;

    const element = document.createElement('a');
    element.setAttribute('href', `data:text/plain;charset=utf-8,${encodeURIComponent(receiptContent)}`);
    element.setAttribute('download', `bank-transfer-${Date.now()}.txt`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Make a Donation</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        {/* Amount Display */}
        <div className="bg-blue-50 p-4 rounded-lg mb-6">
          <p className="text-gray-600 text-sm">Campaign</p>
          <p className="text-lg font-semibold mb-2">{campaignTitle}</p>
          <p className="text-gray-600 text-sm">Amount to Donate</p>
          <p className="text-3xl font-bold text-blue-600">₹{amount}</p>
        </div>

        {/* Payment Method Selection */}
        <div className="space-y-3 mb-6">
          <label className="flex items-center p-3 border-2 border-blue-600 rounded-lg cursor-pointer">
            <input
              type="radio"
              value="razorpay"
              checked={paymentMethod === 'razorpay'}
              onChange={(e) => setPaymentMethod(e.target.value as any)}
            />
            <span className="ml-3">
              <span className="font-semibold">Razorpay</span>
              <p className="text-sm text-gray-600">Debit/Credit Card, UPI, Wallet</p>
            </span>
          </label>

          <label className="flex items-center p-3 border-2 border-gray-300 rounded-lg cursor-pointer">
            <input
              type="radio"
              value="bank_transfer"
              checked={paymentMethod === 'bank_transfer'}
              onChange={(e) => setPaymentMethod(e.target.value as any)}
            />
            <span className="ml-3">
              <span className="font-semibold">Direct Bank Transfer</span>
              <p className="text-sm text-gray-600">Transfer to our bank account</p>
            </span>
          </label>
        </div>

        {/* Bank Transfer Details */}
        {paymentMethod === 'bank_transfer' && bankDetails && (
          <div className="bg-gray-50 p-4 rounded-lg mb-6">
            <h3 className="font-semibold mb-3">Bank Transfer Details</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Account Holder:</span>
                <span className="font-semibold">{bankDetails.bank_account.account_holder_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Account Number:</span>
                <span className="font-mono">{bankDetails.bank_account.account_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">IFSC Code:</span>
                <span className="font-mono">{bankDetails.bank_account.ifsc_code}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Bank Branch:</span>
                <span>{bankDetails.bank_account.bank_branch}</span>
              </div>
            </div>

            <Button
              variant="outline"
              className="w-full mt-3 flex items-center justify-center gap-2"
              onClick={downloadBankTransferReceipt}
            >
              <Download className="w-4 h-4" />
              Download Details
            </Button>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button variant="outline" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={paymentMethod === 'razorpay' ? handleRazorpayPayment : onClose}
            disabled={loading}
            className="flex-1"
          >
            {loading ? 'Processing...' : paymentMethod === 'razorpay' ? 'Pay Now' : 'Proceed'}
          </Button>
        </div>

        {/* Security Notice */}
        <p className="text-xs text-gray-500 text-center mt-4">
          ✓ Secure payment processing
        </p>
      </Card>
    </div>
  );
};

export default PaymentModal;
