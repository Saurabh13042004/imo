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
import { type UserInput } from "@/hooks/useAdminCrud";

interface UserEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: UserInput) => Promise<void>;
  initialData?: Partial<UserInput>;
  isLoading?: boolean;
  title?: string;
}

export const UserEditModal = ({
  isOpen,
  onClose,
  onSubmit,
  initialData,
  isLoading = false,
  title = "Edit User",
}: UserEditModalProps) => {
  const [formData, setFormData] = useState<UserInput>({
    full_name: initialData?.full_name || "",
    email: initialData?.email || "",
    subscription_tier: initialData?.subscription_tier || "free",
    access_level: initialData?.access_level || "basic",
    avatar_url: initialData?.avatar_url || "",
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
      <DialogContent className="bg-white border-slate-200 max-w-md">
        <DialogHeader>
          <DialogTitle className="text-slate-900">{title}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email */}
          <div>
            <Label htmlFor="email" className="text-slate-900">
              Email *
            </Label>
            <Input
              id="email"
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="mt-1 bg-white border-slate-200 text-slate-900"
              disabled={isLoading}
            />
          </div>

          {/* Full Name */}
          <div>
            <Label htmlFor="full_name" className="text-slate-900">
              Full Name
            </Label>
            <Input
              id="full_name"
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              className="mt-1 bg-white border-slate-200 text-slate-900"
              disabled={isLoading}
            />
          </div>

          {/* Subscription Tier */}
          <div>
            <Label htmlFor="subscription_tier" className="text-slate-900">
              Subscription Tier
            </Label>
            <Select
              value={formData.subscription_tier || "free"}
              onValueChange={(value) =>
                setFormData({ ...formData, subscription_tier: value })
              }
              disabled={isLoading}
            >
              <SelectTrigger className="mt-1 bg-white border-slate-200 text-slate-900">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="free">Free</SelectItem>
                <SelectItem value="trial">Trial</SelectItem>
                <SelectItem value="premium">Premium</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Access Level */}
          <div>
            <Label htmlFor="access_level" className="text-slate-900">
              Access Level
            </Label>
            <Select
              value={formData.access_level || "basic"}
              onValueChange={(value) =>
                setFormData({ ...formData, access_level: value })
              }
              disabled={isLoading}
            >
              <SelectTrigger className="mt-1 bg-white border-slate-200 text-slate-900">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="basic">Basic</SelectItem>
                <SelectItem value="admin">Admin</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Avatar URL */}
          <div>
            <Label htmlFor="avatar_url" className="text-slate-900">
              Avatar URL
            </Label>
            <Input
              id="avatar_url"
              type="url"
              value={formData.avatar_url}
              onChange={(e) => setFormData({ ...formData, avatar_url: e.target.value })}
              className="mt-1 bg-white border-slate-200 text-slate-900"
              disabled={isLoading}
            />
          </div>

          {/* Buttons */}
          <div className="flex gap-2 justify-end pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
              className="border-slate-300 text-slate-900"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isLoading ? "Saving..." : "Save"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};
