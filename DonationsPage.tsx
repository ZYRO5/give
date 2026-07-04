import React from 'react';
import { Header, Footer } from '../components/Layout';
import { Card, Button, FormInput } from '../components/UI';
import { DataTable } from '../components/Charts';
import { donationService } from '../services';
import { Gift } from 'lucide-react';

const DonationsPage: React.FC = () => {
  const [donations, setDonations] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [currentPage, setCurrentPage] = React.useState(1);

  React.useEffect(() => {
    const fetchDonations = async () => {
      try {
        const response = await donationService.listDonations((currentPage - 1) * 10, 10);
        setDonations(response.data);
      } catch (error) {
        console.error('Error fetching donations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDonations();
  }, [currentPage]);

  const columns = [
    {
      label: 'Amount',
      key: 'amount',
      render: (value: number) => `$${value.toLocaleString()}`,
    },
    {
      label: 'Payment Method',
      key: 'payment_method',
    },
    {
      label: 'Status',
      key: 'status',
      render: (value: string) => (
        <span className={`px-2 py-1 rounded-full text-xs ${
          value === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
        }`}>
          {value}
        </span>
      ),
    },
    {
      label: 'Date',
      key: 'created_at',
      render: (value: string) => new Date(value).toLocaleDateString(),
    },
  ];

  const actions = [
    { label: 'View', onClick: (row: any) => console.log('View', row.id) },
    { label: 'Receipt', onClick: (row: any) => console.log('Receipt', row.id) },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-8 flex items-center gap-2">
          <Gift className="w-8 h-8" /> Donations
        </h1>

        <Card>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <DataTable columns={columns} data={donations} actions={actions} />
          )}
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default DonationsPage;
