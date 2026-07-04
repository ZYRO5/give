import React from 'react';
import { Header, Footer } from '../components/Layout';
import { Card, Button, StatCard } from '../components/UI';
import PaymentModal from '../components/PaymentModal';
import { donationService } from '../services';
import { Heart, TrendingUp, Users, DollarSign } from 'lucide-react';

const DonatePage: React.FC = () => {
  const [amount, setAmount] = React.useState<number>(500);
  const [customAmount, setCustomAmount] = React.useState<string>('');
  const [showPaymentModal, setShowPaymentModal] = React.useState(false);
  const [selectedCampaign, setSelectedCampaign] = React.useState<any>(null);
  const [campaigns, setCampaigns] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);

  const predefinedAmounts = [100, 250, 500, 1000, 2500, 5000];

  React.useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const response = await donationService.listDonations(0, 5);
      setCampaigns(response.data || []);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAmountSelect = (value: number) => {
    setAmount(value);
    setCustomAmount('');
  };

  const handleCustomAmount = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setCustomAmount(value);
    if (value) {
      setAmount(parseInt(value) || 0);
    }
  };

  const handleDonate = (campaign: any) => {
    setSelectedCampaign(campaign);
    setShowPaymentModal(true);
  };

  const handlePaymentSuccess = () => {
    alert('Thank you for your donation!');
    setShowPaymentModal(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4 flex items-center justify-center gap-2">
            <Heart className="w-10 h-10 text-red-600" />
            Make a Donation
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Your generosity makes a real difference. Choose an amount below and select how you'd like to contribute.
          </p>
        </div>

        {/* Impact Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <StatCard
            label="Total Raised"
            value="₹25,00,000"
            icon={<DollarSign className="w-8 h-8" />}
          />
          <StatCard
            label="Active Campaigns"
            value="12"
            icon={<TrendingUp className="w-8 h-8" />}
          />
          <StatCard
            label="Donors"
            value="3,456"
            icon={<Users className="w-8 h-8" />}
          />
        </div>

        {/* Quick Donation Section */}
        <Card className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Quick Donation</h2>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">Select Amount</label>
            <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
              {predefinedAmounts.map((value) => (
                <button
                  key={value}
                  onClick={() => handleAmountSelect(value)}
                  className={`py-3 px-4 rounded-lg font-semibold transition ${
                    amount === value
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                  }`}
                >
                  ₹{value}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Or Enter Custom Amount</label>
            <div className="relative">
              <span className="absolute left-3 top-3 text-gray-500">₹</span>
              <input
                type="number"
                value={customAmount}
                onChange={handleCustomAmount}
                placeholder="Enter amount"
                className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg mb-6">
            <p className="text-gray-600 text-sm">Amount to Donate</p>
            <p className="text-3xl font-bold text-blue-600">₹{amount}</p>
          </div>

          <Button variant="primary" className="w-full" size="lg" onClick={() => setShowPaymentModal(true)}>
            Proceed to Payment
          </Button>
        </Card>

        {/* Featured Campaigns */}
        {!loading && campaigns.length > 0 && (
          <Card>
            <h2 className="text-2xl font-bold mb-6">Featured Campaigns</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {campaigns.map((campaign) => (
                <div key={campaign.id} className="border rounded-lg p-4 hover:shadow-lg transition">
                  <h3 className="font-bold text-lg mb-2">{campaign.title}</h3>
                  <p className="text-gray-600 text-sm mb-3">{campaign.description}</p>
                  
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600">Progress</span>
                      <span className="font-semibold">
                        {campaign.raised_amount && campaign.target_amount
                          ? Math.round((campaign.raised_amount / campaign.target_amount) * 100)
                          : 0}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{
                          width: `${
                            campaign.raised_amount && campaign.target_amount
                              ? Math.min((campaign.raised_amount / campaign.target_amount) * 100, 100)
                              : 0
                          }%`,
                        }}
                      />
                    </div>
                  </div>

                  <div className="flex justify-between text-sm mb-4">
                    <span className="text-gray-600">Raised: ₹{campaign.raised_amount?.toLocaleString() || 0}</span>
                    <span className="text-gray-600">Goal: ₹{campaign.target_amount?.toLocaleString() || 0}</span>
                  </div>

                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => handleDonate(campaign)}
                  >
                    Donate Now
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        )}
      </main>

      {/* Payment Modal */}
      <PaymentModal
        isOpen={showPaymentModal}
        amount={amount}
        campaignTitle={selectedCampaign?.title || 'General Donation'}
        onClose={() => setShowPaymentModal(false)}
        onPaymentSuccess={handlePaymentSuccess}
      />

      <Footer />
    </div>
  );
};

export default DonatePage;
