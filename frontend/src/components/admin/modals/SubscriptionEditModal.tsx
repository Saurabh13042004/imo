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
import { Checkbox } from "@/components/ui/checkbox";
import { type SubscriptionInput } from "@/hooks/useAdminCrud";

interface SubscriptionEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: SubscriptionInput) => Promise<void>;
  initialData?: Partial<SubscriptionInput>;
  isLoading?: boolean;
  title?: string;
}

export const SubscriptionEditModal = ({
  isOpen,
  onClose,
  onSubmit,
  initialData,
  isLoading = false,
  title = "Edit Subscription",
}: SubscriptionEditModalProps) => {
  const [formData, setFormData] = useState<SubscriptionInput>({
    user_id: initialData?.user_id || "",
    plan_type: initialData?.plan_type || "free",
    billing_cycle: initialData?.billing_cycle || undefined,
    is_active: initialData?.is_active || false,
    subscription_start: initialData?.subscription_start || new Date().toISOString(),
    subscription_end: initialData?.subscription_end || undefined,
    trial_start: initialData?.trial_start || undefined,
    trial_end: initialData?.trial_end || undefined,
    stripe_customer_id: initialData?.stripe_customer_id || undefined,
    stripe_subscription_id: initialData?.stripe_subscription_id || undefined,
    stripe_product_id: initialData?.stripe_product_id || undefined,
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

          {/* Plan Type */}
          <div>
            <Label htmlFor="plan_type" className="text-slate-900 text-sm">
              Plan Type *
            </Label>
            <Select
              value={formData.plan_type}
              onValueChange={(value) => setFormData({ ...formData, plan_type: value })}
              disabled={isLoading}
            >
              <SelectTrigger className="mt-1 bg-white border-slate-200 text-slate-900 text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="free">Free</SelectItem>
                <SelectItem value="trial">Trial</SelectItem>
                <SelectItem value="premium">Premium</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Billing Cycle */}
          <div>
            <Label htmlFor="billing_cycle" className="text-slate-900 text-sm">
              Billing Cycle
            </Label>
            <Select
              value={formData.billing_cycle || ""}
              onValueChange={(value) => setFormData({ ...formData, billing_cycle: value || undefined })}
              disabled={isLoading}
            >
              <SelectTrigger className="mt-1 bg-white border-slate-200 text-slate-900 text-sm">
                <SelectValue placeholder="Select billing cycle" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">None</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="yearly">Yearly</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Is Active */}
          <div className="flex items-center gap-2">
            <Checkbox
              id="is_active"
              checked={formData.is_active}
              onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked as boolean })}
              disabled={isLoading}
            />
            <Label htmlFor="is_active" className="text-slate-900 text-sm cursor-pointer">
              Is Active
            </Label>
          </div>

          {/* Subscription Start */}
          <div>
            <Label htmlFor="subscription_start" className="text-slate-900 text-sm">
              Start Date
            </Label>
            <Input
              id="subscription_start"
              type="datetime-local"
              value={formData.subscription_start?.slice(0, 16) || ""}
              onChange={(e) => setFormData({ ...formData, subscription_start: new Date(e.target.value).toISOString() })}
              className="mt-1 bg-white border-slate-200 text-slate-900 text-sm"
              disabled={isLoading}
            />
          </div>

          {/* Subscription End */}
          <div>
            <Label htmlFor="subscription_end" className="text-slate-900 text-sm">
              End Date
            </Label>
            <Input
              id="subscription_end"
              type="datetime-local"
              value={formData.subscription_end?.slice(0, 16) || ""}
              onChange={(e) => setFormData({ ...formData, subscription_end: e.target.value ? new Date(e.target.value).toISOString() : undefined })}
              className="mt-1 bg-white border-slate-200 text-slate-900 text-sm"
              disabled={isLoading}
            />
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
