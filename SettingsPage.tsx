import React from 'react';
import { Header, Footer } from '../components/Layout';
import { Card, Button, FormInput, Tabs } from '../components/UI';
import { useAuthStore } from '../utils/store';
import { Settings, Lock, Bell, Shield } from 'lucide-react';

const SettingsPage: React.FC = () => {
  const user = useAuthStore((state) => state.user);
  const [displayName, setDisplayName] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [notifications, setNotifications] = React.useState({
    emailOnDonation: true,
    emailOnUpdate: true,
    emailWeeklyDigest: false,
  });

  const tabs = [
    {
      label: 'Profile',
      content: (
        <div className="space-y-4">
          <FormInput label="Display Name" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
          <FormInput label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Button variant="primary">Save Profile</Button>
        </div>
      ),
    },
    {
      label: 'Security',
      content: (
        <div className="space-y-4">
          <FormInput label="Current Password" type="password" placeholder="••••••••" />
          <FormInput label="New Password" type="password" placeholder="••••••••" />
          <FormInput label="Confirm Password" type="password" placeholder="••••••••" />
          <Button variant="primary">Change Password</Button>
        </div>
      ),
    },
    {
      label: 'Notifications',
      content: (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label>Email on Donation</label>
            <input
              type="checkbox"
              checked={notifications.emailOnDonation}
              onChange={(e) => setNotifications({ ...notifications, emailOnDonation: e.target.checked })}
            />
          </div>
          <div className="flex items-center justify-between">
            <label>Email on Campaign Update</label>
            <input
              type="checkbox"
              checked={notifications.emailOnUpdate}
              onChange={(e) => setNotifications({ ...notifications, emailOnUpdate: e.target.checked })}
            />
          </div>
          <div className="flex items-center justify-between">
            <label>Weekly Digest</label>
            <input
              type="checkbox"
              checked={notifications.emailWeeklyDigest}
              onChange={(e) => setNotifications({ ...notifications, emailWeeklyDigest: e.target.checked })}
            />
          </div>
          <Button variant="primary">Save Preferences</Button>
        </div>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-8 flex items-center gap-2">
          <Settings className="w-8 h-8" /> Settings
        </h1>

        <Card>
          <Tabs tabs={tabs} />
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default SettingsPage;
