import { useState } from "react";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TrendingUp, Calendar, Loader2, Edit2, Trash2, Plus } from "lucide-react";
import { useAdminSubscriptions, useAdminPaymentTransactions } from "@/hooks/useAdminApi";
import {
  useCreateSubscription,
  useUpdateSubscription,
  useDeleteSubscription,
  type SubscriptionInput,
} from "@/hooks/useAdminCrud";
import { SubscriptionEditModal } from "./modals/SubscriptionEditModal";

const chartData = [
  { date: "Dec 18", active: 420, trials: 85, revenue: 3200 },
  { date: "Dec 19", active: 425, trials: 92, revenue: 3400 },
  { date: "Dec 20", active: 430, trials: 110, revenue: 3600 },
  { date: "Dec 21", active: 435, trials: 115, revenue: 3800 },
  { date: "Dec 22", active: 440, trials: 118, revenue: 4000 },
  { date: "Dec 23", active: 445, trials: 120, revenue: 4300 },
  { date: "Dec 24", active: 450, trials: 120, revenue: 4500 },
];

export const SubscriptionsTable = () => {
  const [filter, setFilter] = useState<"all" | "active" | "cancelled" | "expired">("all");
  const [editingSubscription, setEditingSubscription] = useState<any | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { data: subData, isLoading: subsLoading } = useAdminSubscriptions(0, 500, filter !== "all" ? filter : undefined);
  const { data: transData, isLoading: transLoading } = useAdminPaymentTransactions(0, 500);

  const createSubscriptionMutation = useCreateSubscription();
  const updateSubscriptionMutation = useUpdateSubscription();
  const deleteSubscriptionMutation = useDeleteSubscription();

  const handleCreate = async (data: SubscriptionInput) => {
    try {
      await createSubscriptionMutation.mutateAsync(data);
      setIsCreateModalOpen(false);
    } catch (error) {
      console.error("Failed to create subscription:", error);
    }
  };

  const handleUpdate = async (data: SubscriptionInput) => {
    if (!editingSubscription) return;
    try {
      await updateSubscriptionMutation.mutateAsync({
        subscriptionId: editingSubscription.id,
        data,
      });
      setEditingSubscription(null);
    } catch (error) {
      console.error("Failed to update subscription:", error);
    }
  };

  const handleDelete = async (subscriptionId: string) => {
    if (!confirm("Are you sure you want to delete this subscription?")) return;
    try {
      await deleteSubscriptionMutation.mutateAsync(subscriptionId);
    } catch (error) {
      console.error("Failed to delete subscription:", error);
    }
  };

  if (subsLoading || transLoading) {
    return <div className="text-center py-8"><Loader2 className="w-8 h-8 animate-spin mx-auto" /></div>;
  }

  const subscriptions = subData?.data || [];
  const transactions = transData?.data || [];

  const activeCount = subscriptions.filter(s => s.isActive).length;
  const totalRevenue = transactions
    .filter(t => t.status === 'success')
    .reduce((sum, t) => sum + (t.amount || 0), 0);
  const pendingTransactions = transactions.filter(t => t.status === 'pending').length;
  const cancelledCount = subscriptions.filter(s => !s.isActive).length;
  const cancellationRate = subscriptions.length > 0 
    ? ((cancelledCount / subscriptions.length) * 100).toFixed(1)
    : '0';

  const getStatusBadgeStyles = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 border-green-300 text-green-700";
      case "cancelled":
        return "bg-red-100 border-red-300 text-red-700";
      case "expired":
        return "bg-slate-100 border-slate-300 text-slate-700";
      default:
        return "bg-slate-100 border-slate-300 text-slate-700";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Create Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-900">Subscriptions</h2>
        <Button
          onClick={() => setIsCreateModalOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Subscription
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          {
            label: "Active Subscriptions",
            value: activeCount,
            icon: TrendingUp,
            color: "from-green-500 to-emerald-500",
          },
          {
            label: "Total Revenue",
            value: `$${totalRevenue.toFixed(2)}`,
            icon: Calendar,
            color: "from-blue-500 to-cyan-500",
          },
          {
            label: "Cancellation Rate",
            value: `${cancellationRate}%`,
            icon: TrendingUp,
            color: "from-orange-500 to-red-500",
          },
        ].map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <Card
              key={idx}
              className="bg-white border-slate-200 p-6 relative overflow-hidden"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-slate-600 text-sm mb-2">{stat.label}</p>
                  <p className="text-2xl font-bold text-slate-900">{stat.value}</p>
                </div>
                <div
                  className={`p-3 rounded-lg bg-gradient-to-br ${stat.color} text-white`}
                >
                  <Icon className="w-5 h-5" />
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Chart */}
      <Card className="bg-white border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Subscription Trends</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="date" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#f8fafc",
                border: "1px solid #e2e8f0",
              }}
              labelStyle={{ color: "#0f172a" }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="active"
              stroke="#059669"
              strokeWidth={2}
              name="Active Subs"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="trials"
              stroke="#d97706"
              strokeWidth={2}
              name="Trials"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Filter Buttons */}
      <div className="flex gap-2">
        {["all", "active", "cancelled", "expired"].map((status) => (
          <Button
            key={status}
            onClick={() => setFilter(status as any)}
            variant={filter === status ? "default" : "outline"}
            className={
              filter === status
                ? ""
                : "border-slate-300 text-slate-700 hover:bg-slate-100"
            }
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </Button>
        ))}
      </div>

      {/* Table */}
      <Card className="bg-white border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-slate-200 hover:bg-transparent">
                <TableHead className="text-slate-900">Customer</TableHead>
                <TableHead className="text-slate-900">Plan Type</TableHead>
                <TableHead className="text-slate-900">Status</TableHead>
                <TableHead className="text-slate-900">Start Date</TableHead>
                <TableHead className="text-slate-900">End Date</TableHead>
                <TableHead className="text-slate-900">Amount</TableHead>
                <TableHead className="text-slate-900">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {subscriptions.slice(0, 5).map((sub, idx) => (
                <motion.tr
                  key={sub.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: idx * 0.05 }}
                  className="border-slate-200 hover:bg-slate-50 transition-colors"
                >
                  <TableCell>
                    <div>
                      <p className="text-slate-900 font-medium">{sub.userEmail?.split('@')[0] || 'User'}</p>
                      <p className="text-xs text-slate-600">{sub.userEmail || 'N/A'}</p>
                    </div>
                  </TableCell>
                  <TableCell className="text-slate-700">{sub.planType || 'Standard'}</TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={sub.isActive ? 'bg-green-100 border-green-300 text-green-700' : 'bg-red-100 border-red-300 text-red-700'}
                    >
                      {sub.isActive ? 'Active' : 'Inactive'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-slate-600">
                    {sub.subscriptionStart ? new Date(sub.subscriptionStart).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell className="text-slate-600">
                    {sub.subscriptionEnd ? new Date(sub.subscriptionEnd).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell className="font-semibold text-slate-900">
                    ${'0.00'}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setEditingSubscription(sub)}
                        className="border-slate-300 hover:bg-slate-100 text-slate-900"
                      >
                        <Edit2 className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(sub.id)}
                        disabled={deleteSubscriptionMutation.isPending}
                        className="border-red-300 hover:bg-red-100 text-red-600"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </motion.tr>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>

      {/* Modals */}
      {isCreateModalOpen && (
        <SubscriptionEditModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSubmit={handleCreate}
          isLoading={createSubscriptionMutation.isPending}
          title="Create Subscription"
        />
      )}

      {editingSubscription && (
        <SubscriptionEditModal
          isOpen={!!editingSubscription}
          onClose={() => setEditingSubscription(null)}
          onSubmit={handleUpdate}
          initialData={{
            user_id: editingSubscription.userId,
            plan_type: editingSubscription.planType,
            billing_cycle: editingSubscription.billingCycle,
            is_active: editingSubscription.isActive,
            subscription_start: editingSubscription.subscriptionStart,
            subscription_end: editingSubscription.subscriptionEnd,
            trial_start: editingSubscription.trialStart,
            trial_end: editingSubscription.trialEnd,
          }}
          isLoading={updateSubscriptionMutation.isPending}
          title="Edit Subscription"
        />
      )}
    </div>
  );
};
