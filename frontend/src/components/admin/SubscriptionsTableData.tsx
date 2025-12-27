import { useState } from "react";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Search, Filter, Loader2 } from "lucide-react";
import { useAdminSubscriptions } from "@/hooks/useAdminApi";

interface Subscription {
  id: string;
  userId: string;
  userEmail: string;
  planType: string;
  billingCycle?: string;
  isActive: boolean;
  subscriptionStart?: string;
  subscriptionEnd?: string;
  trialStart?: string;
  trialEnd?: string;
}

export const SubscriptionsView = () => {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [page, setPage] = useState(0);

  const { data: subscriptionData, isLoading } = useAdminSubscriptions(
    page * 50,
    50,
    statusFilter !== "all" ? (statusFilter === "active" ? "active" : "inactive") : undefined
  );

  if (isLoading) {
    return <div className="text-center py-8"><Loader2 className="w-8 h-8 animate-spin mx-auto" /></div>;
  }

  let subscriptions = subscriptionData?.data || [];

  // Filter by search
  if (search) {
    subscriptions = subscriptions.filter(s =>
      s.userEmail?.toLowerCase().includes(search.toLowerCase()) ||
      s.id?.toLowerCase().includes(search.toLowerCase())
    );
  }

  const activeCount = subscriptions.filter(s => s.isActive).length;
  const inactiveCount = subscriptions.filter(s => !s.isActive).length;
  const premiumCount = subscriptions.filter(s => s.planType === 'premium').length;

  const getPlanBadgeStyles = (planType: string) => {
    switch (planType?.toLowerCase()) {
      case "premium":
        return "bg-purple-100 border-purple-300 text-purple-700";
      case "trial":
        return "bg-orange-100 border-orange-300 text-orange-700";
      case "standard":
        return "bg-blue-100 border-blue-300 text-blue-700";
      default:
        return "bg-slate-100 border-slate-300 text-slate-700";
    }
  };

  const getStatusBadgeStyles = (isActive: boolean) => {
    return isActive
      ? "bg-green-100 border-green-300 text-green-700"
      : "bg-red-100 border-red-300 text-red-700";
  };

  const getRemainingDays = (endDate?: string) => {
    if (!endDate) return "N/A";
    const end = new Date(endDate);
    const now = new Date();
    const diff = Math.floor((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    if (diff < 0) return "Expired";
    return `${diff} days`;
  };

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: "Total Subscriptions", value: subscriptionData?.total?.toString() || '0', color: "bg-blue-50 border-blue-200" },
          { label: "Active", value: activeCount.toString(), color: "bg-green-50 border-green-200" },
          { label: "Inactive", value: inactiveCount.toString(), color: "bg-red-50 border-red-200" },
          { label: "Premium Plans", value: premiumCount.toString(), color: "bg-purple-50 border-purple-200" },
        ].map((stat, idx) => (
          <div key={idx} className={`rounded-lg border ${stat.color} p-6`}>
            <p className="text-sm text-slate-600 font-medium">{stat.label}</p>
            <p className="text-2xl font-bold text-slate-900 mt-2">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            placeholder="Search by email or subscription ID..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
            className="pl-10 bg-white border-slate-200 text-slate-900 placeholder:text-slate-500"
          />
        </div>
        <Select value={statusFilter} onValueChange={(val) => {
          setStatusFilter(val);
          setPage(0);
        }}>
          <SelectTrigger className="w-full sm:w-40 bg-white border-slate-200 text-slate-900">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Subscriptions Table */}
      <Card className="bg-white border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-slate-200 hover:bg-transparent">
                <TableHead className="text-slate-900">User Email</TableHead>
                <TableHead className="text-slate-900">Plan Type</TableHead>
                <TableHead className="text-slate-900">Status</TableHead>
                <TableHead className="text-slate-900">Start Date</TableHead>
                <TableHead className="text-slate-900">End Date</TableHead>
                <TableHead className="text-slate-900">Remaining</TableHead>
                <TableHead className="text-slate-900">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {subscriptions.map((sub, idx) => (
                <motion.tr
                  key={sub.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: idx * 0.05 }}
                  className="border-slate-200 hover:bg-slate-50 transition-colors"
                >
                  <TableCell className="font-medium">
                    <div>
                      <p className="text-slate-900">{sub.userEmail}</p>
                      <p className="text-xs text-slate-600 font-mono">{sub.userId?.substring(0, 12)}...</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={getPlanBadgeStyles(sub.planType)}
                    >
                      {(sub.planType || 'unknown').charAt(0).toUpperCase() + (sub.planType || 'unknown').slice(1)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={getStatusBadgeStyles(sub.isActive)}
                    >
                      {sub.isActive ? 'Active' : 'Inactive'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-slate-600 text-sm">
                    {sub.subscriptionStart ? new Date(sub.subscriptionStart).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell className="text-slate-600 text-sm">
                    {sub.subscriptionEnd ? new Date(sub.subscriptionEnd).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell className="text-slate-600 text-sm">
                    {getRemainingDays(sub.subscriptionEnd)}
                  </TableCell>
                  <TableCell>
                    <Button
                      size="sm"
                      variant="outline"
                      className="border-slate-300 hover:bg-slate-100 text-slate-900"
                    >
                      Manage
                    </Button>
                  </TableCell>
                </motion.tr>
              ))}
            </TableBody>
          </Table>
        </div>
        {subscriptions.length === 0 && (
          <div className="text-center py-8 text-slate-500">
            No subscriptions found
          </div>
        )}
      </Card>

      {/* Pagination */}
      <div className="flex gap-2 justify-center">
        <Button
          onClick={() => setPage(Math.max(0, page - 1))}
          disabled={page === 0}
          variant="outline"
        >
          Previous
        </Button>
        <span className="px-4 py-2 text-slate-900">Page {page + 1}</span>
        <Button
          onClick={() => setPage(page + 1)}
          disabled={(page + 1) * 50 >= (subscriptionData?.total || 0)}
          variant="outline"
        >
          Next
        </Button>
      </div>
    </div>
  );
};
