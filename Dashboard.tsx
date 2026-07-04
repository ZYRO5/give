import React from 'react';
import { Header, Footer } from '../components/Layout';
import { Card, StatCard } from '../components/UI';
import { BarChartComponent, LineChartComponent } from '../components/Charts';
import { useDashboardStore } from '../utils/store';
import { reportService } from '../services';
import { DollarSign, Users, Target, TrendingUp } from 'lucide-react';

const Dashboard: React.FC = () => {
  const [stats, setStats] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchStats = async () => {
      try {
        const summary = await reportService.getDashboardSummary();
        setStats(summary.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return <div className="min-h-screen bg-gray-50 p-8">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            label="Total Raised"
            value={`$${stats?.total_raised?.toLocaleString() || 0}`}
            icon={<DollarSign className="w-8 h-8" />}
            trend={{ value: 12, direction: 'up' }}
          />
          <StatCard
            label="Active Donors"
            value={stats?.total_donors || 0}
            icon={<Users className="w-8 h-8" />}
            trend={{ value: 8, direction: 'up' }}
          />
          <StatCard
            label="Active Campaigns"
            value={stats?.total_campaigns || 0}
            icon={<Target className="w-8 h-8" />}
            trend={{ value: 15, direction: 'up' }}
          />
          <StatCard
            label="Total Donations"
            value={stats?.total_donations || 0}
            icon={<TrendingUp className="w-8 h-8" />}
            trend={{ value: 25, direction: 'up' }}
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <BarChartComponent
            data={[
              { month: 'Jan', donations: 40 },
              { month: 'Feb', donations: 30 },
              { month: 'Mar', donations: 50 },
            ]}
            dataKey="donations"
            xKey="month"
            title="Donations This Month"
          />

          <LineChartComponent
            data={[
              { month: 'Jan', revenue: 4000 },
              { month: 'Feb', revenue: 3000 },
              { month: 'Mar', revenue: 5000 },
            ]}
            dataKey="revenue"
            xKey="month"
            title="Revenue Trend"
          />
        </div>

        {/* Recent Activity */}
        <Card className="mt-8">
          <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
          <div className="space-y-2">
            <p className="text-gray-600">5 new donations received</p>
            <p className="text-gray-600">2 new campaigns created</p>
            <p className="text-gray-600">3 donors registered</p>
          </div>
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default Dashboard;
