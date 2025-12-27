import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { type TransactionInput } from "@/hooks/useAdminCrud";

interface TransactionEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: TransactionInput) => Promise<void>;
  initialData?: Partial<TransactionInput>;
  isLoading?: boolean;
  title?: string;
}

export const TransactionEditModal = ({
  isOpen,
  onClose,
  onSubmit,
  initialData,
  isLoading = false,
  title = "Edit Transaction",
}: TransactionEditModalProps) => {
  const [formData, setFormData] = useState<TransactionInput>({
    user_id: initialData?.user_id || "",
    subscription_id: initialData?.subscription_id || undefined,
    transaction_id: initialData?.transaction_id || "",
    amount: initialData?.amount || 0,
    currency: initialData?.currency || "usd",
    type: initialData?.type || "subscription",
    status: initialData?.status || "pending",
    stripe_payment_intent_id: initialData?.stripe_payment_intent_id || undefined,
    stripe_session_id: initialData?.stripe_session_id || undefined,
    metadata_json: initialData?.metadata_json || undefined,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error("Error submitting form:", error);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-white border-slate-200 max-w-md max-h-96 overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-slate-900">{title}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-3">
          {/* User ID */}
          <div>
            <Label htmlFor="user_id" className="text-slate-900 text-sm">
              User ID *
            </Label>
            <Input
              id="user_id"
              type="text"
              required
              value={formData.user_id}
              onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
              className="mt-1 bg-white border-slate-200 text-slate-900 text-sm"
              disabled={isLoading || !!initialData}
              placeholder="UUID"
            />
          </div>

          {/* Transaction ID */}
          <div>
            <Label htmlFor="transaction_id" className="text-slate-900 text-sm">
              Transaction ID *
            </Label>
            <Input
              id="transaction_id"
              type="text"
              required
              value={formData.transaction_id}
              onChange={(e) => setFormData({ ...formData, transaction_id: e.target.value })}
              className="mt-1 bg-white border-slate-200 text-slate-900 text-sm"
              disabled={isLoading}
            />
          </div>

          {/* Amount */}
          <div>
            <Label htmlFor="amount" className="text-slate-900 text-sm">
              Amount *
            </Label>
            <Input
              id="amount"
              type="number"
              step="0.01"
              required
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
              className="mt-1 bg-white border-slate-200 text-slate-900 text-sm"
              disabled={isLoading}
            />
          </div>

          {/* Currency */}
          <div>
            <Label htmlFor="currency" className="text-slate-900 text-sm">
              Currency
            </Label>
            <Input
              id="currency"
              type="text"
              value={formData.currency}
              onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
              className="mt-1 bg-white border-slate-200 text-slate-900 text-sm"
              disabled={isLoading}
            />
          </div>

          {/* Type */}
          <div>
            <Label htmlFor="type" className="text-slate-900 text-sm">
              Type *
            </Label>
            <Select
              value={formData.type}
              onValueChange={(value) => setFormData({ ...formData, type: value })}
              disabled={isLoading}
            >
              <SelectTrigger className="mt-1 bg-white border-slate-200 text-slate-900 text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="subscription">Subscription</SelectItem>
                <SelectItem value="one_time">One Time</SelectItem>
                <SelectItem value="refund">Refund</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Status */}
          <div>
            <Label htmlFor="status" className="text-slate-900 text-sm">
              Status
            </Label>
            <Select
              value={formData.status}
              onValueChange={(value) => setFormData({ ...formData, status: value })}
              disabled={isLoading}
            >
              <SelectTrigger className="mt-1 bg-white border-slate-200 text-slate-900 text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="success">Success</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
                <SelectItem value="refunded">Refunded</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Buttons */}
          <div className="flex gap-2 justify-end pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
              className="border-slate-300 text-slate-900 text-sm"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white text-sm"
            >
              {isLoading ? "Saving..." : "Save"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};
