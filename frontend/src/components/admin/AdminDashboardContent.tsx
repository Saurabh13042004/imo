import { useState } from "react";
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
} from "lucide-react";
import { motion } from "framer-motion";
import { AdminStats } from "./AdminStats";
import { useAdminStats } from "@/hooks/useAdminApi";

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

export const AdminDashboardContent = () => {
  const { data: stats, isLoading, error } = useAdminStats();
  const [hoveredMetric, setHoveredMetric] = useState<string | null>(null);

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

      {/* Revenue and System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Trend */}
        <Card className="bg-white border border-slate-200 p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Revenue Trend</h3>
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
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: "#3b82f6", r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="subscriptions"
                stroke="#10b981"
                strokeWidth={2}
                dot={{ fill: "#10b981", r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* System Health */}
        <Card className="bg-white border border-slate-200 p-6 hover:shadow-lg transition-shadow">
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
              <Bar dataKey="value" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Recent Activities */}
      <Card className="bg-white border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Recent Activities</h3>
        <div className="space-y-3">
          {[
            {
              event: "New Premium Subscription",
              user: "john@example.com",
              time: "2 hours ago",
              type: "success",
              icon: TrendingUp,
            },
            {
              event: "Trial Conversion",
              user: "sarah@example.com",
              time: "4 hours ago",
              type: "success",
              icon: Activity,
            },
            {
              event: "User Signup",
              user: "mike@example.com",
              time: "6 hours ago",
              type: "info",
              icon: Activity,
            },
            {
              event: "Payment Failed",
              user: "jane@example.com",
              time: "8 hours ago",
              type: "warning",
              icon: AlertCircle,
            },
            {
              event: "API Rate Limit Alert",
              user: "system@imo.com",
              time: "12 hours ago",
              type: "warning",
              icon: AlertCircle,
            },
          ].map((activity, idx) => {
            const Icon = activity.icon;
            const bgColor =
              activity.type === "success"
                ? "bg-green-50 border-l-4 border-green-500"
                : activity.type === "warning"
                  ? "bg-yellow-50 border-l-4 border-yellow-500"
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
          })}
        </div>
      </Card>
    </div>
  );
};
