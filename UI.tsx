import React from 'react';
import { AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';

interface AlertProps {
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
  onClose?: () => void;
}

export const Alert: React.FC<AlertProps> = ({ type, title, message, onClose }) => {
  const bgColors = {
    success: 'bg-green-50',
    error: 'bg-red-50',
    info: 'bg-blue-50',
    warning: 'bg-yellow-50',
  };

  const borderColors = {
    success: 'border-green-200',
    error: 'border-red-200',
    info: 'border-blue-200',
    warning: 'border-yellow-200',
  };

  const textColors = {
    success: 'text-green-800',
    error: 'text-red-800',
    info: 'text-blue-800',
    warning: 'text-yellow-800',
  };

  const icons = {
    success: <CheckCircle className="w-5 h-5" />,
    error: <AlertCircle className="w-5 h-5" />,
    info: <Info className="w-5 h-5" />,
    warning: <AlertTriangle className="w-5 h-5" />,
  };

  return (
    <div className={`${bgColors[type]} ${borderColors[type]} border rounded-lg p-4 flex gap-3`}>
      <div className={textColors[type]}>{icons[type]}</div>
      <div className="flex-1">
        <h3 className={`${textColors[type]} font-semibold`}>{title}</h3>
        <p className={`${textColors[type]} text-sm mt-1`}>{message}</p>
      </div>
      {onClose && (
        <button onClick={onClose} className={`${textColors[type]} hover:opacity-70`}>
          ×
        </button>
      )}
    </div>
  );
};

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  ...props
}) => {
  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-green-600 hover:bg-green-700 text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50',
  };

  const sizeClasses = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`${variantClasses[variant]} ${sizeClasses[size]} rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? 'Loading...' : children}
    </button>
  );
};

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ children, className = '' }) => (
  <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
    {children}
  </div>
);

interface FormInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const FormInput: React.FC<FormInputProps> = ({ label, error, ...props }) => (
  <div className="space-y-2">
    {label && <label className="block text-sm font-medium text-gray-700">{label}</label>}
    <input
      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
        error ? 'border-red-500' : 'border-gray-300'
      }`}
      {...props}
    />
    {error && <p className="text-sm text-red-500">{error}</p>}
  </div>
);

interface ModalProps {
  isOpen: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({ isOpen, title, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{title}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={`${sizeClasses[size]} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin`} />
  );
};

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({ currentPage, totalPages, onPageChange }) => (
  <div className="flex justify-center gap-2 mt-6">
    <Button
      variant="outline"
      onClick={() => onPageChange(currentPage - 1)}
      disabled={currentPage === 1}
    >
      Previous
    </Button>
    {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
      <Button
        key={page}
        variant={currentPage === page ? 'primary' : 'outline'}
        onClick={() => onPageChange(page)}
      >
        {page}
      </Button>
    ))}
    <Button
      variant="outline"
      onClick={() => onPageChange(currentPage + 1)}
      disabled={currentPage === totalPages}
    >
      Next
    </Button>
  </div>
);

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
}

export const StatCard: React.FC<StatCardProps> = ({ label, value, icon, trend }) => (
  <Card>
    <div className="flex justify-between items-start">
      <div>
        <p className="text-gray-600 text-sm">{label}</p>
        <p className="text-3xl font-bold mt-2">{value}</p>
        {trend && (
          <p className={`text-sm mt-2 ${trend.direction === 'up' ? 'text-green-600' : 'text-red-600'}`}>
            {trend.direction === 'up' ? '↑' : '↓'} {Math.abs(trend.value)}%
          </p>
        )}
      </div>
      {icon && <div className="text-gray-400">{icon}</div>}
    </div>
  </Card>
);

interface TabsProps {
  tabs: Array<{ label: string; content: React.ReactNode }>;
  defaultTab?: number;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, defaultTab = 0 }) => {
  const [activeTab, setActiveTab] = React.useState(defaultTab);

  return (
    <div>
      <div className="flex gap-2 border-b">
        {tabs.map((tab, index) => (
          <button
            key={index}
            onClick={() => setActiveTab(index)}
            className={`px-4 py-2 font-medium ${
              activeTab === index
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="mt-4">{tabs[activeTab].content}</div>
    </div>
  );
};
