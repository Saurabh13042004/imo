import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
} from "recharts";
import {
  TrendingUp,
  Activity,
  Clock,
  AlertCircle,
  Loader2,
  Lock,
} from "lucide-react";
import { motion } from "framer-motion";
import { AdminStats } from "./AdminStats";
import { useAdminStats } from "@/hooks/useAdminApi";
import { useAuth } from "@/hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import { API_BASE_URL } from "@/config/api";

const revenueData = [
  { month: "Jan", revenue: 3200, subscriptions: 240 },
  { month: "Feb", revenue: 3800, subscriptions: 280 },
  { month: "Mar", revenue: 4500, subscriptions: 320 },
  { month: "Apr", revenue: 4200, subscriptions: 310 },
  { month: "May", revenue: 5100, subscriptions: 380 },
  { month: "Jun", revenue: 5900, subscriptions: 420 },
];

const systemHealthData = [
  { name: "API Time", value: 87, target: 100 },
  { name: "DB Uptime", value: 99.98, target: 100 },
  { name: "Cache Hit", value: 94, target: 100 },
  { name: "Memory", value: 72, target: 100 },
];

// Fetch monthly revenue from admin stats
async function fetchMonthlyRevenue(accessToken: string) {
  console.log('📊 fetchMonthlyRevenue called with token:', !!accessToken);
  const url = `${API_BASE_URL}/api/v1/admin/stats`;
  console.log('📍 Fetching from:', url);
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });
  if (!response.ok) throw new Error('Failed to fetch admin stats');
  const data = await response.json();
  console.log('✅ Monthly revenue fetched:', data.monthlyRevenue);
  return data.monthlyRevenue || 0;
}

// Fetch recent activities (transactions, trials, logins)
async function fetchRecentActivities(accessToken: string) {
  console.log('=== fetchRecentActivities called with token:', !!accessToken);
  try {
    if (!accessToken) {
      console.warn('⚠️ No auth token available');
      return [];
    }

    const url = `${API_BASE_URL}/api/v1/admin/recent-activities?limit=5`;
    console.log('🔍 Fetching recent activities from:', url);

    const response = await fetch(url, {
      method: 'GET',
      headers: { 
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    });

    console.log('📡 Recent activities response status:', response.status);

    // Handle both 200 and 304 (cached) responses
    if (!response.ok && response.status !== 304) {
      const errorText = await response.text();
      console.error('❌ Failed to fetch activities:', response.status, response.statusText, errorText);
      return [];
    }

    const data = await response.json();
    console.log('✅ Recent activities data received:', data);
    
    if (!data.activities || !Array.isArray(data.activities)) {
      console.warn('⚠️ No activities array in response:', data);
      return [];
    }

    const formattedActivities = data.activities.map((activity: any) => {
      let icon = Activity; // default
      if (activity.type === 'success') {
        icon = TrendingUp;
      } else if (activity.type === 'warning') {
        icon = AlertCircle;
      }

      return {
        event: activity.event || 'Unknown Event',
        user: activity.user || 'Unknown User',
        time: activity.timestamp 
          ? new Date(activity.timestamp).toLocaleDateString('en-US', { 
              month: 'short', 
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })
          : 'Unknown',
        type: activity.type,
        icon,
      };
    });

    console.log('📋 Formatted activities:', formattedActivities);
    return formattedActivities;
  } catch (error) {
    console.error('💥 Error fetching activities:', error);
    return [];
  }
}

export const AdminDashboardContent = () => {
  const { accessToken } = useAuth();
  const { data: stats, isLoading, error } = useAdminStats();
  const [hoveredMetric, setHoveredMetric] = useState<string | null>(null);
  const [monthlyRevenue, setMonthlyRevenue] = useState<number>(0);
  const [monthlyRevenueLoading, setMonthlyRevenueLoading] = useState(true);

  const { data: recentActivities = [], isLoading: activitiesLoading, refetch: refetchActivities } = useQuery({
    queryKey: ['recent-activities', accessToken],
    queryFn: () => fetchRecentActivities(accessToken || ''),
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: 1000 * 60 * 2, // Auto-refetch every 2 minutes
    retry: 2,
    enabled: !!accessToken, // Only enable when we have a token
  });

  // Log when activities are loaded
  useEffect(() => {
    console.log('Recent activities updated:', recentActivities);
  }, [recentActivities]);

  // Initial fetch of activities on mount
  useEffect(() => {
    console.log('AdminDashboardContent mounted, triggering activities fetch');
    refetchActivities();
  }, [refetchActivities]);

  // Calculate monthly revenue from admin stats
  useEffect(() => {
    if (!accessToken) {
      console.warn('⚠️ No access token available for revenue fetch');
      return;
    }

    const calculateRevenue = async () => {
      try {
        const revenue = await fetchMonthlyRevenue(accessToken);
        setMonthlyRevenue(revenue);
      } catch (err) {
        console.error('Error fetching monthly revenue:', err);
        // Fall back to showing 0 if fetch fails
        setMonthlyRevenue(0);
      } finally {
        setMonthlyRevenueLoading(false);
      }
    };

    calculateRevenue();
  }, [accessToken]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto text-slate-400 mb-4" />
          <p className="text-slate-600">Loading statistics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-red-700">
        <p className="font-semibold">Failed to load statistics</p>
        <p className="text-sm mt-2">Please try refreshing the page</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <AdminStats stats={stats || {
        totalUsers: 0,
        totalSubscriptions: 0,
        activeTrials: 0,
        monthlyRevenue: 0,
        totalUrls: 0,
        apiCalls: 0,
      }} />

      {/* Monthly Revenue Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 p-6 hover:shadow-lg transition-shadow text-white">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Monthly Revenue</h3>
            <Badge className="bg-green-500 text-white hover:bg-green-600">
              <TrendingUp className="w-3 h-3 mr-1" />
              ↑ 12%
            </Badge>
          </div>
          {monthlyRevenueLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin" />
            </div>
          ) : (
            <div>
              <p className="text-4xl font-bold mb-2">${monthlyRevenue.toFixed(2)}</p>
              <p className="text-slate-300 text-sm">Based on active subscriptions</p>
            </div>
          )}
        </Card>
      </motion.div>

      {/* Revenue Comparison and System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Trend */}
        <Card className="bg-white border border-slate-200 p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Revenue Trend (Last 6 Months)</h3>
            <Badge className="bg-green-100 text-green-700 hover:bg-green-100">
              <TrendingUp className="w-3 h-3 mr-1" />
              +12% this month
            </Badge>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#ffffff",
                  border: "1px solid #e2e8f0",
                  borderRadius: "8px",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#000000"
                strokeWidth={2}
                dot={{ fill: "#000000", r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="subscriptions"
                stroke="#666666"
                strokeWidth={2}
                dot={{ fill: "#666666", r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* System Health - Under Dev (Blurred) */}
        <div className="relative">
          <Card className="bg-white border border-slate-200 p-6 hover:shadow-lg transition-shadow blur-sm opacity-50">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-900">System Health</h3>
              <Badge className="bg-green-100 text-green-700 hover:bg-green-100">
                All Systems Healthy
              </Badge>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={systemHealthData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#ffffff",
                    border: "1px solid #e2e8f0",
                    borderRadius: "8px",
                  }}
                />
                <Bar dataKey="value" fill="#000000" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="bg-yellow-100 border border-yellow-400 px-4 py-2 rounded-lg flex items-center gap-2 text-yellow-800 font-medium">
              <Lock className="w-4 h-4" />
              Under Development
            </div>
          </div>
        </div>
      </div>

      {/* Development Cards - Blurred */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Total URLs - Under Dev (Blurred) */}
        <div className="relative">
          <Card className="bg-white border border-slate-200 p-6 blur-sm opacity-50">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Total URLs</h3>
            <p className="text-4xl font-bold text-slate-900">4,140</p>
            <p className="text-slate-600 text-sm mt-2">Indexed URLs across platform</p>
          </Card>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="bg-yellow-100 border border-yellow-400 px-4 py-2 rounded-lg flex items-center gap-2 text-yellow-800 font-medium">
              <Lock className="w-4 h-4" />
              Under Development
            </div>
          </div>
        </div>

        {/* API Calls - Under Dev (Blurred) */}
        <div className="relative">
          <Card className="bg-white border border-slate-200 p-6 blur-sm opacity-50">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">API Calls</h3>
            <p className="text-4xl font-bold text-slate-900">0.0M</p>
            <p className="text-slate-600 text-sm mt-2">Monthly API requests</p>
          </Card>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="bg-yellow-100 border border-yellow-400 px-4 py-2 rounded-lg flex items-center gap-2 text-yellow-800 font-medium">
              <Lock className="w-4 h-4" />
              Under Development
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activities */}
      <Card className="bg-white border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900">Recent Activities</h3>
          {activitiesLoading && (
            <Loader2 className="w-4 h-4 animate-spin text-slate-600" />
          )}
        </div>
        <div className="space-y-3">
          {activitiesLoading && recentActivities.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
              <p>Loading activities...</p>
            </div>
          ) : recentActivities && recentActivities.length > 0 ? (
            recentActivities.map((activity: any, idx: number) => {
              const Icon = activity.icon;
              const bgColor =
                activity.type === "success"
                  ? "bg-green-50 border-l-4 border-green-500"
                  : activity.type === "warning"
                    ? "bg-red-50 border-l-4 border-red-500"
                    : "bg-blue-50 border-l-4 border-blue-500";

              return (
                <motion.div
                  key={idx}
                  className={`${bgColor} p-4 rounded-lg flex items-start gap-4`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <Icon className="w-5 h-5 text-slate-600 mt-1 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900">{activity.event}</p>
                    <p className="text-xs text-slate-600 mt-1">{activity.user}</p>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <Clock className="w-4 h-4 text-slate-400" />
                    <span className="text-xs text-slate-500 whitespace-nowrap">{activity.time}</span>
                  </div>
                </motion.div>
              );
            })
          ) : (
            <div className="text-center py-8 text-slate-500">
              <p>No recent activities</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};
