import React from 'react';
import { Header, Footer } from '../components/Layout';
import { Card, Button, FormInput, Pagination } from '../components/UI';
import { DataTable } from '../components/Charts';
import { campaignService } from '../services';
import { Plus, Edit2, Trash2 } from 'lucide-react';

const CampaignsPage: React.FC = () => {
  const [campaigns, setCampaigns] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [currentPage, setCurrentPage] = React.useState(1);
  const [searchQuery, setSearchQuery] = React.useState('');

  React.useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        const response = await campaignService.listCampaigns((currentPage - 1) * 10, 10);
        setCampaigns(response.data);
      } catch (error) {
        console.error('Error fetching campaigns:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCampaigns();
  }, [currentPage]);

  const columns = [
    {
      label: 'Title',
      key: 'title',
      render: (value: string) => <div className="font-semibold">{value}</div>,
    },
    {
      label: 'Target Amount',
      key: 'target_amount',
      render: (value: number) => `$${value.toLocaleString()}`,
    },
    {
      label: 'Raised',
      key: 'raised_amount',
      render: (value: number) => `$${value.toLocaleString()}`,
    },
    {
      label: 'Status',
      key: 'status',
      render: (value: string) => (
        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
          value === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
        }`}>
          {value}
        </span>
      ),
    },
  ];

  const actions = [
    { label: 'Edit', onClick: (row: any) => console.log('Edit', row.id) },
    { label: 'Delete', onClick: (row: any) => console.log('Delete', row.id) },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Campaigns</h1>
          <Button variant="primary" size="md">
            <Plus className="w-4 h-4 mr-2 inline" /> New Campaign
          </Button>
        </div>

        <Card className="mb-6">
          <div className="flex gap-4 mb-4">
            <FormInput
              placeholder="Search campaigns..."
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
            <>
              <DataTable columns={columns} data={campaigns} actions={actions} />
              <Pagination currentPage={currentPage} totalPages={10} onPageChange={setCurrentPage} />
            </>
          )}
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default CampaignsPage;
