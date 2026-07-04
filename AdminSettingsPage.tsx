import React from 'react';
import { Header, Footer } from '../components/Layout';
import { Card, Button, FormInput, Tabs } from '../components/UI';
import { Settings, Copy, Check } from 'lucide-react';
import { copyToClipboard } from '../utils/helpers';

const AdminSettingsPage: React.FC = () => {
  const [copied, setCopied] = React.useState<string | null>(null);
  const [bankDetails] = React.useState({
    accountNumber: '42818590419',
    accountHolder: 'Pallapu Vinod',
    accountType: 'Savings Account',
    ifscCode: 'SBIN0021400',
    bankBranch: 'VENKATARAMANA COLONY, KURNOOL',
    bank: 'State Bank of India (SBI)',
  });

  const [ownerInfo] = React.useState({
    email: 'vinod1914581@gmail.com',
    name: 'Pallapu Vinod',
    organization: 'Donor Platform',
  });

  const handleCopy = async (text: string, label: string) => {
    const success = await copyToClipboard(text);
    if (success) {
      setCopied(label);
      setTimeout(() => setCopied(null), 2000);
    }
  };

  const tabs = [
    {
      label: 'Owner Information',
      content: (
        <div className="space-y-4">
          <FormInput
            label="Email"
            type="email"
            value={ownerInfo.email}
            disabled
          />
          <FormInput
            label="Name"
            value={ownerInfo.name}
            disabled
          />
          <FormInput
            label="Organization"
            value={ownerInfo.organization}
            disabled
          />
          <Button variant="outline">Edit Profile</Button>
        </div>
      ),
    },
    {
      label: 'Bank Account Details',
      content: (
        <div className="space-y-4">
          <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mb-4">
            <p className="text-sm text-yellow-800">
              ⚠️ Bank details are confidential. Share carefully and only with authorized recipients.
            </p>
          </div>

          <div className="space-y-3">
            {[
              { label: 'Account Number', value: bankDetails.accountNumber, key: 'accountNumber' },
              { label: 'Account Holder', value: bankDetails.accountHolder, key: 'accountHolder' },
              { label: 'Account Type', value: bankDetails.accountType, key: 'accountType' },
              { label: 'IFSC Code', value: bankDetails.ifscCode, key: 'ifscCode' },
              { label: 'Bank Branch', value: bankDetails.bankBranch, key: 'bankBranch' },
              { label: 'Bank', value: bankDetails.bank, key: 'bank' },
            ].map(({ label, value, key }) => (
              <div key={key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-600">{label}</p>
                  <p className="font-mono font-semibold">{value}</p>
                </div>
                <button
                  onClick={() => handleCopy(value, key)}
                  className="p-2 hover:bg-gray-200 rounded"
                  title="Copy to clipboard"
                >
                  {copied === key ? (
                    <Check className="w-5 h-5 text-green-600" />
                  ) : (
                    <Copy className="w-5 h-5 text-gray-600" />
                  )}
                </button>
              </div>
            ))}
          </div>

          <Button variant="outline">Edit Bank Details</Button>
        </div>
      ),
    },
    {
      label: 'Payment Configuration',
      content: (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg mb-4">
            <p className="text-sm text-blue-800">
              💡 Payment gateways configured in .env file. Update environment variables to enable additional payment methods.
            </p>
          </div>

          <div className="space-y-3">
            <div className="p-3 bg-gray-50 rounded-lg flex items-center justify-between">
              <div>
                <h3 className="font-semibold">Razorpay</h3>
                <p className="text-sm text-gray-600">Primary payment gateway (Enabled)</p>
              </div>
              <div className="w-3 h-3 bg-green-600 rounded-full"></div>
            </div>

            <div className="p-3 bg-gray-50 rounded-lg flex items-center justify-between">
              <div>
                <h3 className="font-semibold">Bank Transfer</h3>
                <p className="text-sm text-gray-600">Direct bank transfer option (Enabled)</p>
              </div>
              <div className="w-3 h-3 bg-green-600 rounded-full"></div>
            </div>

            <div className="p-3 bg-gray-50 rounded-lg flex items-center justify-between opacity-50">
              <div>
                <h3 className="font-semibold">Stripe</h3>
                <p className="text-sm text-gray-600">Add in payment configuration (Disabled)</p>
              </div>
              <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
            </div>

            <div className="p-3 bg-gray-50 rounded-lg flex items-center justify-between opacity-50">
              <div>
                <h3 className="font-semibold">PayPal</h3>
                <p className="text-sm text-gray-600">Add in payment configuration (Disabled)</p>
              </div>
              <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
            </div>
          </div>

          <Button variant="outline">Configure Payment Gateways</Button>
        </div>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-8 flex items-center gap-2">
          <Settings className="w-8 h-8" />
          Admin Settings
        </h1>

        <Card>
          <Tabs tabs={tabs} />
        </Card>

        {/* Payment Setup Guide */}
        <Card className="mt-8">
          <h2 className="text-xl font-bold mb-4">Payment Setup Guide</h2>
          <div className="space-y-4 text-gray-600">
            <p>
              ✓ Owner email configured: <strong>{ownerInfo.email}</strong>
            </p>
            <p>
              ✓ Bank account details configured: <strong>{bankDetails.accountHolder}</strong>
            </p>
            <p>
              ✓ Razorpay payment gateway ready
            </p>
            <p>
              Next: Configure Razorpay API keys in environment variables for live payment processing.
            </p>
            <a
              href="/PAYMENT_SETUP.md"
              className="text-blue-600 hover:underline font-semibold"
            >
              → Read Payment Setup Guide
            </a>
          </div>
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default AdminSettingsPage;
