import React from 'react';
import { Header, Footer } from '../components/Layout';
import { Card, Button, FormInput } from '../components/UI';
import { DataTable } from '../components/Charts';
import { donorService } from '../services';
import { Users, TrendingUp } from 'lucide-react';

const DonorsPage: React.FC = () => {
  const [donors, setDonors] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [searchQuery, setSearchQuery] = React.useState('');

  React.useEffect(() => {
    const fetchDonors = async () => {
      try {
        const response = await donorService.listDonors(0, 20);
        setDonors(response.data);
      } catch (error) {
        console.error('Error fetching donors:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDonors();
  }, []);

  const columns = [
    {
      label: 'Donor Type',
      key: 'donor_type',
    },
    {
      label: 'Total Donated',
      key: 'total_donated',
      render: (value: number) => `$${value.toLocaleString()}`,
    },
    {
      label: 'Donations Count',
      key: 'donation_count',
    },
    {
      label: 'Status',
      key: 'status',
      render: (value: string) => (
        <span className={`px-2 py-1 rounded-full text-xs ${
          value === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100'
        }`}>
          {value}
        </span>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-8 flex items-center gap-2">
          <Users className="w-8 h-8" /> Donors
        </h1>

        <Card className="mb-6">
          <div className="flex gap-4">
            <FormInput
              placeholder="Search donors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <Button variant="outline">Search</Button>
          </div>
        </Card>

        <Card>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <DataTable columns={columns} data={donors} />
          )}
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default DonorsPage;
