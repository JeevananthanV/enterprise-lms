import React, { useState } from 'react';
import {
  Search,
  Mail,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import { Tabs } from '../../components/common/Tabs';
import { Modal } from '../../components/common/Modal';
import { useToast } from '../../context/ToastContext';

interface UserRecord {
  id: number;
  email: string;
  full_name: string;
  role: 'STUDENT' | 'INSTRUCTOR' | 'PLATFORM_ADMIN';
  is_active: boolean;
  created_at?: string;
}

export const UserManagementPage: React.FC = () => {
  const { showSuccess, showInfo } = useToast();
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');
  const [selectedUser, setSelectedUser] = useState<UserRecord | null>(null);

  // Mock initial enterprise user set or fetch from backend
  const users: UserRecord[] = [
    { id: 1, email: 'admin@example.com', full_name: 'Platform Administrator', role: 'PLATFORM_ADMIN', is_active: true, created_at: '2026-09-01T10:00:00Z' },
    { id: 2, email: 'instructor.alice@example.com', full_name: 'Alice Johnson', role: 'INSTRUCTOR', is_active: true, created_at: '2026-09-02T11:30:00Z' },
    { id: 3, email: 'instructor.bob@example.com', full_name: 'Bob Smith', role: 'INSTRUCTOR', is_active: true, created_at: '2026-09-03T14:15:00Z' },
    { id: 4, email: 'student.charlie@example.com', full_name: 'Charlie Brown', role: 'STUDENT', is_active: true, created_at: '2026-09-04T09:20:00Z' },
    { id: 5, email: 'student.diana@example.com', full_name: 'Diana Prince', role: 'STUDENT', is_active: true, created_at: '2026-09-05T16:45:00Z' },
    { id: 6, email: 'student.edward@example.com', full_name: 'Edward Norton', role: 'STUDENT', is_active: false, created_at: '2026-09-06T12:00:00Z' },
  ];

  const filteredUsers = users.filter((u) => {
    const matchesSearch =
      u.full_name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase());
    const matchesRole = roleFilter === 'ALL' || u.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const handleRoleChange = (newRole: string) => {
    showSuccess('User Role Updated', `Role for ${selectedUser?.email} updated to ${newRole}`);
    setSelectedUser(null);
  };

  const handleStatusToggle = (user: UserRecord) => {
    showInfo('Status Toggled', `${user.full_name} is now ${user.is_active ? 'Inactive' : 'Active'}`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            User Governance & RBAC
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Manage user accounts, assign roles, enforce platform security policies and view account status.
          </p>
        </div>
        <Button
          variant="primary"
          size="sm"
          onClick={() => showInfo('Invite User', 'User invitation link copied to clipboard')}
        >
          <Mail className="w-4 h-4 mr-1.5" />
          Invite New User
        </Button>
      </div>

      {/* Filter Tabs */}
      <Tabs
        tabs={[
          { id: 'ALL', label: 'All Accounts', count: users.length },
          { id: 'STUDENT', label: 'Students', count: users.filter((u) => u.role === 'STUDENT').length },
          { id: 'INSTRUCTOR', label: 'Instructors', count: users.filter((u) => u.role === 'INSTRUCTOR').length },
          { id: 'PLATFORM_ADMIN', label: 'Admins', count: users.filter((u) => u.role === 'PLATFORM_ADMIN').length },
        ]}
        activeTab={roleFilter}
        onChange={setRoleFilter}
      />

      {/* Search Input */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative max-w-sm w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100 transition-all shadow-xs"
          />
        </div>
        <span className="text-xs text-slate-500 font-medium">
          Showing {filteredUsers.length} of {users.length} users
        </span>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/80 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <th className="py-3.5 px-4">User</th>
                <th className="py-3.5 px-4">Role</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Created Date</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {filteredUsers.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs ${
                          u.role === 'PLATFORM_ADMIN'
                            ? 'bg-rose-600'
                            : u.role === 'INSTRUCTOR'
                            ? 'bg-amber-600'
                            : 'bg-sky-600'
                        }`}
                      >
                        {u.full_name[0]}
                      </div>
                      <div>
                        <p className="font-semibold text-slate-900 leading-tight">{u.full_name}</p>
                        <p className="text-[11px] text-slate-500">{u.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <Badge
                      variant={
                        u.role === 'PLATFORM_ADMIN'
                          ? 'error'
                          : u.role === 'INSTRUCTOR'
                          ? 'warning'
                          : 'info'
                      }
                    >
                      {u.role}
                    </Badge>
                  </td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium ${
                        u.is_active
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-slate-100 text-slate-500 border border-slate-200'
                      }`}
                    >
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${
                          u.is_active ? 'bg-emerald-500' : 'bg-slate-400'
                        }`}
                      />
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-500">
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedUser(u)}
                        className="text-[11px] py-1"
                      >
                        Manage
                      </Button>
                      <button
                        onClick={() => handleStatusToggle(u)}
                        title={u.is_active ? 'Deactivate user' : 'Activate user'}
                        className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                      >
                        {u.is_active ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <AlertCircle className="w-4 h-4 text-rose-500" />}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* User Manage Modal */}
      {selectedUser && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedUser(null)}
          title={`User Governance: ${selectedUser.full_name}`}
          subtitle={`Account ID #${selectedUser.id} • ${selectedUser.email}`}
          maxWidth="md"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Assign System Role
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['STUDENT', 'INSTRUCTOR', 'PLATFORM_ADMIN'] as const).map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => handleRoleChange(r)}
                    className={`py-2 px-3 text-xs font-semibold rounded-xl border transition-all ${
                      selectedUser.role === r
                        ? 'bg-sky-50 border-sky-500 text-sky-700 ring-2 ring-sky-200'
                        : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1.5 text-slate-600">
              <p>
                <span className="font-semibold text-slate-800">Authoritative RBAC Notice:</span> Role changes take effect immediately on the next token refresh or API request.
              </p>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={() => setSelectedUser(null)}>
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
