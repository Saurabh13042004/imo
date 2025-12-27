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
import { Search, Filter, ChevronUp, ChevronDown, Loader2, Edit2, Trash2, Plus } from "lucide-react";
import { useAdminUsers } from "@/hooks/useAdminApi";
import { useCreateUser, useUpdateUser, useDeleteUser, type UserInput } from "@/hooks/useAdminCrud";
import { UserEditModal } from "./modals/UserEditModal";

export const UsersTable = () => {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(0);
  const [editingUser, setEditingUser] = useState<any | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const { data: userData, isLoading } = useAdminUsers(page * 50, 50, search || undefined, filter !== "all" ? filter : undefined);

  const createUserMutation = useCreateUser();
  const updateUserMutation = useUpdateUser();
  const deleteUserMutation = useDeleteUser();

  const handleCreate = async (data: UserInput) => {
    try {
      await createUserMutation.mutateAsync(data);
      setIsCreateModalOpen(false);
    } catch (error) {
      console.error("Failed to create user:", error);
    }
  };

  const handleUpdate = async (data: UserInput) => {
    if (!editingUser) return;
    try {
      await updateUserMutation.mutateAsync({
        userId: editingUser.id,
        data,
      });
      setEditingUser(null);
    } catch (error) {
      console.error("Failed to update user:", error);
    }
  };

  const handleDelete = async (userId: string) => {
    if (!confirm("Are you sure you want to delete this user?")) return;
    try {
      console.log("[UsersTable] Deleting user:", userId);
      await deleteUserMutation.mutateAsync(userId);
      console.log("[UsersTable] User deleted successfully");
    } catch (error: any) {
      console.error("[UsersTable] Failed to delete user:", {
        message: error?.message,
        response: error?.response?.data,
        status: error?.response?.status,
        headers: error?.response?.headers,
        fullError: error,
      });
    }
  };

  if (isLoading) {
    return <div className="text-center py-8"><Loader2 className="w-8 h-8 animate-spin mx-auto" /></div>;
  }

  const users = userData?.data || [];

  const getTierBadgeStyles = (tier: string) => {
    switch (tier) {
      case "premium":
        return "bg-purple-100 border-purple-300 text-purple-700";
      case "trial":
        return "bg-orange-100 border-orange-300 text-orange-700";
      default:
        return "bg-slate-100 border-slate-300 text-slate-700";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Create Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-900">Users</h2>
        <Button
          onClick={() => setIsCreateModalOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create User
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
            className="pl-10 bg-white border-slate-200 text-slate-900 placeholder:text-slate-500"
          />
        </div>
        <Select value={filter} onValueChange={(val) => {
          setFilter(val);
          setPage(0);
        }}>
          <SelectTrigger className="w-full sm:w-40 bg-white border-slate-200 text-slate-900">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Users</SelectItem>
            <SelectItem value="premium">Premium</SelectItem>
            <SelectItem value="trial">Trial</SelectItem>
            <SelectItem value="free">Free</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      <Card className="bg-white border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-slate-200 hover:bg-transparent">
                <TableHead className="text-slate-900">User</TableHead>
                <TableHead className="text-slate-900">Tier</TableHead>
                <TableHead className="text-slate-900">Join Date</TableHead>
                <TableHead className="text-slate-900">Last Active</TableHead>
                <TableHead className="text-slate-900">Status</TableHead>
                <TableHead className="text-slate-900">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user, idx) => (
                <motion.tr
                  key={user.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: idx * 0.05 }}
                  className="border-slate-200 hover:bg-slate-50 transition-colors"
                >
                  <TableCell className="font-medium">
                    <div>
                      <p className="text-slate-900">{user.name || user.email}</p>
                      <p className="text-xs text-slate-600">{user.email}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={getTierBadgeStyles(user.subscriptionTier || 'free')}
                    >
                      {(user.subscriptionTier || 'free').charAt(0).toUpperCase() + (user.subscriptionTier || 'free').slice(1)}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-slate-600">
                    {user.joinDate ? new Date(user.joinDate).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell className="text-slate-600">
                    {user.lastActive ? new Date(user.lastActive).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="bg-green-100 border-green-300 text-green-700">
                      Active
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setEditingUser(user)}
                        className="border-slate-300 hover:bg-slate-100 text-slate-900"
                      >
                        <Edit2 className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(user.id)}
                        disabled={deleteUserMutation.isPending}
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

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: "Total Users Shown", value: users.length },
          { label: "Total Users in DB", value: userData?.total || 0 },
          { label: "Current Page", value: page + 1 },
        ].map((stat, idx) => (
          <Card
            key={idx}
            className="bg-white border-slate-200 p-4 text-center"
          >
            <p className="text-slate-600 text-sm mb-2">{stat.label}</p>
            <p className="text-2xl font-bold text-slate-900">{stat.value}</p>
          </Card>
        ))}
      </div>

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
          disabled={(page + 1) * 50 >= (userData?.total || 0)}
          variant="outline"
        >
          Next
        </Button>
      </div>

      {/* Modals */}
      {isCreateModalOpen && (
        <UserEditModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSubmit={handleCreate}
          isLoading={createUserMutation.isPending}
          title="Create User"
        />
      )}

      {editingUser && (
        <UserEditModal
          isOpen={!!editingUser}
          onClose={() => setEditingUser(null)}
          onSubmit={handleUpdate}
          initialData={{
            full_name: editingUser.name,
            email: editingUser.email,
            subscription_tier: editingUser.subscriptionTier,
            access_level: editingUser.accessLevel,
            avatar_url: editingUser.avatar_url,
          }}
          isLoading={updateUserMutation.isPending}
          title="Edit User"
        />
      )}
    </div>
  );
};
