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
import { Search, Filter, Loader2, Edit2, Trash2, Plus } from "lucide-react";
import { useAdminPaymentTransactions } from "@/hooks/useAdminApi";
import { useCreateTransaction, useUpdateTransaction, useDeleteTransaction, type TransactionInput } from "@/hooks/useAdminCrud";
import { TransactionEditModal } from "./modals/TransactionEditModal";

interface Transaction {
  id: string;
  userEmail: string;
  amount: number;
  currency: string;
  type: string;
  status: string;
  createdAt: string;
}

export const TransactionsTable = () => {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [page, setPage] = useState(0);
  const [editingTransaction, setEditingTransaction] = useState<any | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const { data: transactionData, isLoading } = useAdminPaymentTransactions(page * 50, 50);

  const createTransactionMutation = useCreateTransaction();
  const updateTransactionMutation = useUpdateTransaction();
  const deleteTransactionMutation = useDeleteTransaction();

  const handleCreate = async (data: TransactionInput) => {
    try {
      await createTransactionMutation.mutateAsync(data);
      setIsCreateModalOpen(false);
    } catch (error) {
      console.error("Failed to create transaction:", error);
    }
  };

  const handleUpdate = async (data: TransactionInput) => {
    if (!editingTransaction) return;
    try {
      await updateTransactionMutation.mutateAsync({
        transactionId: editingTransaction.id,
        data,
      });
      setEditingTransaction(null);
    } catch (error) {
      console.error("Failed to update transaction:", error);
    }
  };

  const handleDelete = async (transactionId: string) => {
    if (!confirm("Are you sure you want to delete this transaction?")) return;
    try {
      await deleteTransactionMutation.mutateAsync(transactionId);
    } catch (error) {
      console.error("Failed to delete transaction:", error);
    }
  };

  if (isLoading) {
    return <div className="text-center py-8"><Loader2 className="w-8 h-8 animate-spin mx-auto" /></div>;
  }

  let transactions = transactionData?.data || [];

  // Filter by search
  if (search) {
    transactions = transactions.filter(t =>
      t.userEmail?.toLowerCase().includes(search.toLowerCase()) ||
      t.id?.toLowerCase().includes(search.toLowerCase())
    );
  }

  // Filter by type
  if (typeFilter !== "all") {
    transactions = transactions.filter(t => t.type === typeFilter);
  }

  // Filter by status - default to success
  if (statusFilter !== "all") {
    transactions = transactions.filter(t => t.status === statusFilter);
  }

  const getStatusBadgeStyles = (status: string) => {
    switch (status) {
      case "success":
        return "bg-green-100 border-green-300 text-green-700";
      case "failed":
        return "bg-red-100 border-red-300 text-red-700";
      case "pending":
        return "bg-yellow-100 border-yellow-300 text-yellow-700";
      default:
        return "bg-slate-100 border-slate-300 text-slate-700";
    }
  };

  const getTypeBadgeStyles = (type: string) => {
    switch (type) {
      case "subscription":
        return "bg-blue-100 border-blue-300 text-blue-700";
      case "unlock":
        return "bg-purple-100 border-purple-300 text-purple-700";
      default:
        return "bg-slate-100 border-slate-300 text-slate-700";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Create Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-900">Transactions</h2>
        <Button
          onClick={() => setIsCreateModalOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Transaction
        </Button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-white border-slate-200 p-4">
          <div className="text-sm text-slate-600">Total Amount</div>
          <div className="text-2xl font-bold text-slate-900">
            ${transactions.reduce((sum, t) => sum + (t.amount || 0), 0).toFixed(2)}
          </div>
        </Card>
        <Card className="bg-white border-slate-200 p-4">
          <div className="text-sm text-slate-600">Success</div>
          <div className="text-2xl font-bold text-green-600">
            {transactions.filter((t) => t.status === "success").length}
          </div>
        </Card>
        <Card className="bg-white border-slate-200 p-4">
          <div className="text-sm text-slate-600">Pending</div>
          <div className="text-2xl font-bold text-yellow-600">
            {transactions.filter((t) => t.status === "pending").length}
          </div>
        </Card>
        <Card className="bg-white border-slate-200 p-4">
          <div className="text-sm text-slate-600">Failed</div>
          <div className="text-2xl font-bold text-red-600">
            {transactions.filter((t) => t.status === "failed").length}
          </div>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            placeholder="Search by email or transaction ID..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
            className="pl-10 bg-white border-slate-200 text-slate-900 placeholder:text-slate-500"
          />
        </div>
        <Select value={typeFilter} onValueChange={(val) => {
          setTypeFilter(val);
          setPage(0);
        }}>
          <SelectTrigger className="w-full sm:w-40 bg-white border-slate-200 text-slate-900">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="subscription">Subscription</SelectItem>
            <SelectItem value="unlock">Unlock</SelectItem>
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={(val) => {
          setStatusFilter(val);
          setPage(0);
        }}>
          <SelectTrigger className="w-full sm:w-40 bg-white border-slate-200 text-slate-900">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="success">Success Only</SelectItem>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Transactions Table */}
      <Card className="bg-white border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-slate-200 hover:bg-transparent">
                <TableHead className="text-slate-900">Transaction ID</TableHead>
                <TableHead className="text-slate-900">User Email</TableHead>
                <TableHead className="text-slate-900">Amount</TableHead>
                <TableHead className="text-slate-900">Type</TableHead>
                <TableHead className="text-slate-900">Status</TableHead>
                <TableHead className="text-slate-900">Date</TableHead>
                <TableHead className="text-slate-900">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map((txn, idx) => (
                <motion.tr
                  key={txn.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: idx * 0.05 }}
                  className="border-slate-200 hover:bg-slate-50 transition-colors"
                >
                  <TableCell className="font-mono text-sm text-slate-700">
                    {txn.id?.substring(0, 12)}...
                  </TableCell>
                  <TableCell className="text-slate-700">
                    {txn.userEmail}
                  </TableCell>
                  <TableCell className="font-semibold text-slate-900">
                    ${txn.amount?.toFixed(2) || '0.00'}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={getTypeBadgeStyles(txn.type || 'unknown')}
                    >
                      {(txn.type || 'unknown').charAt(0).toUpperCase() + (txn.type || 'unknown').slice(1)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={getStatusBadgeStyles(txn.status || 'unknown')}
                    >
                      {(txn.status || 'unknown').charAt(0).toUpperCase() + (txn.status || 'unknown').slice(1)}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-slate-600 text-sm">
                    {txn.createdAt ? new Date(txn.createdAt).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setEditingTransaction(txn)}
                        className="border-slate-300 hover:bg-slate-100 text-slate-900"
                      >
                        <Edit2 className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(txn.id)}
                        disabled={deleteTransactionMutation.isPending}
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
        {transactions.length === 0 && (
          <div className="text-center py-8 text-slate-500">
            No transactions found
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
          disabled={(page + 1) * 50 >= (transactionData?.total || 0)}
          variant="outline"
        >
          Next
        </Button>
      </div>

      {/* Modals */}
      {isCreateModalOpen && (
        <TransactionEditModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSubmit={handleCreate}
          isLoading={createTransactionMutation.isPending}
          title="Create Transaction"
        />
      )}

      {editingTransaction && (
        <TransactionEditModal
          isOpen={!!editingTransaction}
          onClose={() => setEditingTransaction(null)}
          onSubmit={handleUpdate}
          initialData={{
            user_id: editingTransaction.userId,
            subscription_id: editingTransaction.subscriptionId,
            transaction_id: editingTransaction.id,
            amount: editingTransaction.amount,
            currency: editingTransaction.currency,
            type: editingTransaction.type,
            status: editingTransaction.status,
          }}
          isLoading={updateTransactionMutation.isPending}
          title="Edit Transaction"
        />
      )}
    </div>
  );
};
