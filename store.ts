import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  loading: false,
  error: null,
  
  login: async (email: string, password: string) => {
    set({ loading: true, error: null });
    try {
      // Call API
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      
      if (!response.ok) throw new Error('Login failed');
      
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      
      set({
        token: data.access_token,
        isAuthenticated: true,
        loading: false,
      });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },
  
  setUser: (user: User) => set({ user }),
  setToken: (token: string) => set({ token, isAuthenticated: true }),
}));

interface NotificationState {
  notifications: any[];
  unreadCount: number;
  addNotification: (notification: any) => void;
  removeNotification: (id: string) => void;
  markAsRead: (id: string) => void;
  clearAll: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  unreadCount: 0,
  
  addNotification: (notification: any) => {
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: state.unreadCount + 1,
    }));
  },
  
  removeNotification: (id: string) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }));
  },
  
  markAsRead: (id: string) => {
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, is_read: true } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    }));
  },
  
  clearAll: () => {
    set({ notifications: [], unreadCount: 0 });
  },
}));

interface DashboardState {
  dashboardData: any | null;
  loading: boolean;
  error: string | null;
  fetchDashboard: () => Promise<void>;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  dashboardData: null,
  loading: false,
  error: null,
  
  fetchDashboard: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch('/api/v1/reports/dashboard/summary');
      if (!response.ok) throw new Error('Failed to fetch dashboard');
      const data = await response.json();
      set({ dashboardData: data, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },
}));
