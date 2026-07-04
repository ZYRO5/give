import React from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface BarChartComponentProps {
  data: any[];
  dataKey: string;
  xKey: string;
  title?: string;
}

export const BarChartComponent: React.FC<BarChartComponentProps> = ({ data, dataKey, xKey, title }) => (
  <div className="bg-white rounded-lg shadow-md p-4">
    {title && <h3 className="text-lg font-bold mb-4">{title}</h3>}
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey={dataKey} fill="#3B82F6" />
      </BarChart>
    </ResponsiveContainer>
  </div>
);

interface LineChartComponentProps {
  data: any[];
  dataKey: string;
  xKey: string;
  title?: string;
}

export const LineChartComponent: React.FC<LineChartComponentProps> = ({ data, dataKey, xKey, title }) => (
  <div className="bg-white rounded-lg shadow-md p-4">
    {title && <h3 className="text-lg font-bold mb-4">{title}</h3>}
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey={dataKey} stroke="#3B82F6" dot={{ r: 4 }} />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

interface PieChartComponentProps {
  data: any[];
  dataKey: string;
  nameKey: string;
  title?: string;
  colors?: string[];
}

export const PieChartComponent: React.FC<PieChartComponentProps> = ({
  data,
  dataKey,
  nameKey,
  title,
  colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'],
}) => (
  <div className="bg-white rounded-lg shadow-md p-4">
    {title && <h3 className="text-lg font-bold mb-4">{title}</h3>}
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={data} dataKey={dataKey} nameKey={nameKey} cx="50%" cy="50%" outerRadius={80} label>
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  </div>
);

interface DonationTrendProps {
  data: Array<{ month: string; donations: number; amount: number }>;
}

export const DonationTrend: React.FC<DonationTrendProps> = ({ data }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
    <BarChartComponent data={data} dataKey="donations" xKey="month" title="Donations Count" />
    <LineChartComponent data={data} dataKey="amount" xKey="month" title="Donation Amount" />
  </div>
);

interface CampaignProgressProps {
  raised: number;
  target: number;
  title?: string;
}

export const CampaignProgress: React.FC<CampaignProgressProps> = ({ raised, target, title }) => {
  const percentage = (raised / target) * 100;

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      {title && <h3 className="text-lg font-bold mb-4">{title}</h3>}
      <div className="mb-2">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-700">Progress</span>
          <span className="font-semibold">{percentage.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${percentage}%` }} />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 mt-4">
        <div>
          <p className="text-sm text-gray-600">Raised</p>
          <p className="text-lg font-bold">${raised.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Target</p>
          <p className="text-lg font-bold">${target.toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
};

interface DataTableProps<T> {
  columns: Array<{
    label: string;
    key: string;
    render?: (value: any, row: T) => React.ReactNode;
  }>;
  data: T[];
  actions?: Array<{
    label: string;
    onClick: (row: T) => void;
  }>;
}

export const DataTable = React.forwardRef<HTMLTableElement, DataTableProps<any>>(
  ({ columns, data, actions }, ref) => (
    <div className="overflow-x-auto">
      <table ref={ref} className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-100 border-b">
            {columns.map((col) => (
              <th key={col.key} className="px-4 py-2 text-left font-semibold text-gray-700">
                {col.label}
              </th>
            ))}
            {actions && <th className="px-4 py-2 text-center font-semibold text-gray-700">Actions</th>}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} className="border-b hover:bg-gray-50">
              {columns.map((col) => (
                <td key={col.key} className="px-4 py-3 text-gray-800">
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
              {actions && (
                <td className="px-4 py-3 text-center">
                  {actions.map((action) => (
                    <button
                      key={action.label}
                      onClick={() => action.onClick(row)}
                      className="text-blue-600 hover:text-blue-800 mr-2"
                    >
                      {action.label}
                    </button>
                  ))}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
);
