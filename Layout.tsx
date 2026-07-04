import React from 'react';
import { Link } from 'react-router-dom';
import { Bell, Settings, LogOut, Menu, X } from 'lucide-react';
import { useAuthStore } from '../utils/store';

export const Header: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  const { user, logout } = useAuthStore();

  return (
    <header className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-2xl font-bold text-blue-600">
            DonorHub
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex gap-6">
            <Link to="/" className="text-gray-700 hover:text-blue-600">
              Dashboard
            </Link>
            <Link to="/campaigns" className="text-gray-700 hover:text-blue-600">
              Campaigns
            </Link>
            <Link to="/donors" className="text-gray-700 hover:text-blue-600">
              Donors
            </Link>
            <Link to="/reports" className="text-gray-700 hover:text-blue-600">
              Reports
            </Link>
          </nav>

          {/* Right Section */}
          <div className="flex items-center gap-4">
            <button className="relative text-gray-600 hover:text-gray-800">
              <Bell className="w-6 h-6" />
              <span className="absolute top-0 right-0 w-2 h-2 bg-red-600 rounded-full" />
            </button>
            <button className="text-gray-600 hover:text-gray-800">
              <Settings className="w-6 h-6" />
            </button>
            <button
              onClick={logout}
              className="text-gray-600 hover:text-gray-800"
            >
              <LogOut className="w-6 h-6" />
            </button>

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden text-gray-600"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden pb-4 border-t">
            <Link to="/" className="block py-2 text-gray-700 hover:text-blue-600">
              Dashboard
            </Link>
            <Link to="/campaigns" className="block py-2 text-gray-700 hover:text-blue-600">
              Campaigns
            </Link>
            <Link to="/donors" className="block py-2 text-gray-700 hover:text-blue-600">
              Donors
            </Link>
            <Link to="/reports" className="block py-2 text-gray-700 hover:text-blue-600">
              Reports
            </Link>
          </nav>
        )}
      </div>
    </header>
  );
};

export const Sidebar: React.FC = () => {
  return (
    <aside className="hidden lg:block w-64 bg-gray-900 text-white p-6 h-screen overflow-y-auto">
      <h2 className="text-xl font-bold mb-8">Navigation</h2>
      <nav className="space-y-4">
        <Link to="/" className="block py-2 px-4 rounded hover:bg-gray-800">
          Dashboard
        </Link>
        <Link to="/campaigns" className="block py-2 px-4 rounded hover:bg-gray-800">
          Campaigns
        </Link>
        <Link to="/donors" className="block py-2 px-4 rounded hover:bg-gray-800">
          Donors
        </Link>
        <Link to="/donations" className="block py-2 px-4 rounded hover:bg-gray-800">
          Donations
        </Link>
        <Link to="/reports" className="block py-2 px-4 rounded hover:bg-gray-800">
          Reports
        </Link>
        <Link to="/settings" className="block py-2 px-4 rounded hover:bg-gray-800">
          Settings
        </Link>
      </nav>
    </aside>
  );
};

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-white mt-12 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="text-lg font-bold mb-4">DonorHub</h3>
            <p className="text-gray-400">Comprehensive donor management platform for nonprofits.</p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-white">Features</a></li>
              <li><a href="#" className="hover:text-white">Pricing</a></li>
              <li><a href="#" className="hover:text-white">Documentation</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-white">About</a></li>
              <li><a href="#" className="hover:text-white">Blog</a></li>
              <li><a href="#" className="hover:text-white">Contact</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-white">Privacy</a></li>
              <li><a href="#" className="hover:text-white">Terms</a></li>
              <li><a href="#" className="hover:text-white">License</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 pt-8 flex justify-between items-center">
          <p className="text-gray-400">&copy; {currentYear} DonorHub. All rights reserved.</p>
          <div className="flex gap-4">
            <a href="#" className="text-gray-400 hover:text-white">Twitter</a>
            <a href="#" className="text-gray-400 hover:text-white">LinkedIn</a>
            <a href="#" className="text-gray-400 hover:text-white">GitHub</a>
          </div>
        </div>
      </div>
    </footer>
  );
};
