import React from 'react';
import { Header, Footer } from '../components/Layout';
import { Card, StatCard, Tabs } from '../components/UI';
import { BarChartComponent, LineChartComponent, PieChartComponent } from '../components/Charts';
import { reportService } from '../services';
import { BarChart3, PieChart, TrendingUp } from 'lucide-react';

const ReportsPage: React.FC = () => {
  const [donorsReport, setDonorsReport] = React.useState<any>(null);
  const [campaignsReport, setCampaignsReport] = React.useState<any>(null);
  const [donationsReport, setDonationsReport] = React.useState<any>(null);
  const [financialSummary, setFinancialSummary] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchReports = async () => {
      try {
        const [donors, campaigns, donations, financial] = await Promise.all([
          reportService.getDonorsReport(),
          reportService.getCampaignsReport(),
          reportService.getDonationsReport(),
          reportService.getFinancialSummary(),
        ]);

        setDonorsReport(donors.data);
        setCampaignsReport(campaigns.data);
        setDonationsReport(donations.data);
        setFinancialSummary(financial.data);
      } catch (error) {
        console.error('Error fetching reports:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  if (loading) {
    return <div className="min-h-screen bg-gray-50 p-8">Loading...</div>;
  }

  const tabs = [
    {
      label: 'Donors',
      content: (
        <div>
          <h3 className="text-xl font-bold mb-4">Donor Report</h3>
          <p className="text-gray-600">Total Donors: {donorsReport?.total_donors}</p>
          <p className="text-gray-600">Total Donated: ${donorsReport?.total_donated?.toLocaleString()}</p>
        </div>
      ),
    },
    {
      label: 'Campaigns',
      content: (
        <div>
          <h3 className="text-xl font-bold mb-4">Campaign Report</h3>
          <p className="text-gray-600">Total Campaigns: {campaignsReport?.total_campaigns}</p>
          <p className="text-gray-600">Total Raised: ${campaignsReport?.total_raised?.toLocaleString()}</p>
        </div>
      ),
    },
    {
      label: 'Donations',
      content: (
        <div>
          <h3 className="text-xl font-bold mb-4">Donation Report</h3>
          <p className="text-gray-600">Total Donations: {donationsReport?.total_donations}</p>
          <p className="text-gray-600">Total Amount: ${donationsReport?.total_amount?.toLocaleString()}</p>
        </div>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-8">Reports & Analytics</h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard
            label="Total Revenue"
            value={`$${financialSummary?.total_revenue?.toLocaleString() || 0}`}
            icon={<TrendingUp className="w-8 h-8" />}
          />
          <StatCard
            label="Total Campaigns"
            value={campaignsReport?.total_campaigns || 0}
            icon={<BarChart3 className="w-8 h-8" />}
          />
          <StatCard
            label="Total Donors"
            value={donorsReport?.total_donors || 0}
            icon={<PieChart className="w-8 h-8" />}
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <BarChartComponent
            data={[
              { month: 'Jan', value: 1000 },
              { month: 'Feb', value: 1500 },
              { month: 'Mar', value: 2000 },
              { month: 'Apr', value: 2500 },
            ]}
            dataKey="value"
            xKey="month"
            title="Monthly Revenue"
          />

          <LineChartComponent
            data={[
              { month: 'Jan', donors: 10 },
              { month: 'Feb', donors: 15 },
              { month: 'Mar', donors: 20 },
              { month: 'Apr', donors: 25 },
            ]}
            dataKey="donors"
            xKey="month"
            title="Donor Growth"
          />
        </div>

        {/* Tabs */}
        <Card>
          <Tabs tabs={tabs} />
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default ReportsPage;
