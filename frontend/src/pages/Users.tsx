import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi } from '../api/client';
import { useAuthStore } from '../store/authStore';
import { Users as UsersIcon, Shield, UserCog, Mail, Building, Edit2, UserX, UserCheck, Loader2 } from 'lucide-react';
import UserFormModal from '../components/UserFormModal';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'officer' | 'developer';
  department: string;
  district?: string;
  is_active: boolean;
  created_at: string;
}

export default function Users() {
  const { user: currentUser } = useAuthStore();
  const queryClient = useQueryClient();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [deactivatingId, setDeactivatingId] = useState<string | null>(null);
  const [reactivatingId, setReactivatingId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const { data: users, isLoading } = useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      const res = await usersApi.list();
      return res.data;
    },
    enabled: currentUser?.role === 'admin' || currentUser?.role === 'officer',
  });

  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => usersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setIsCreateModalOpen(false);
      showToast('User created successfully', 'success');
    },
    onError: (error: unknown) => {
      const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to create user';
      showToast(message, 'error');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) => usersApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setEditingUser(null);
      showToast('User updated successfully', 'success');
    },
    onError: (error: unknown) => {
      const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to update user';
      showToast(message, 'error');
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: (id: string) => usersApi.deactivate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      showToast('User deactivated', 'success');
    },
    onError: (error: unknown) => {
      const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to deactivate user';
      showToast(message, 'error');
    },
    onSettled: () => {
      setDeactivatingId(null);
    },
  });

  const reactivateMutation = useMutation({
    mutationFn: (id: string) => usersApi.update(id, { is_active: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      showToast('User reactivated', 'success');
    },
    onError: (error: unknown) => {
      const message = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to reactivate user';
      showToast(message, 'error');
    },
    onSettled: () => {
      setReactivatingId(null);
    },
  });

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleCreateSubmit = async (formData: Record<string, unknown>) => {
    await createMutation.mutateAsync(formData);
  };

  const handleEditSubmit = async (formData: Record<string, unknown>) => {
    if (editingUser) {
      await updateMutation.mutateAsync({ id: editingUser.id, data: formData });
    }
  };

  const handleDeactivate = (user: User) => {
    if (window.confirm(`Are you sure you want to deactivate ${user.full_name || user.email}?`)) {
      setDeactivatingId(user.id);
      deactivateMutation.mutate(user.id);
    }
  };

  const handleReactivate = (user: User) => {
    setReactivatingId(user.id);
    reactivateMutation.mutate(user.id);
  };

  const roleColors: Record<string, string> = {
    admin: 'bg-purple-500/20 text-purple-400',
    officer: 'bg-blue-500/20 text-blue-400',
    developer: 'bg-green-500/20 text-green-400',
  };

  const roleIcons: Record<string, React.ReactNode> = {
    admin: <Shield size={14} />,
    officer: <UserCog size={14} />,
    developer: <UsersIcon size={14} />,
  };

  const isAdmin = currentUser?.role === 'admin';

  if (currentUser?.role === 'developer') {
    return (
      <div className="p-8 text-center">
        <h2 className="text-xl font-bold text-slate-300">Access Denied</h2>
        <p className="text-slate-500 mt-2">You don't have permission to view this page.</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg ${
            toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'
          } text-white`}
        >
          {toast.message}
        </div>
      )}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">User Management</h1>
          <p className="text-sm text-slate-500 mt-1">Manage system users and their roles</p>
        </div>
        {isAdmin && (
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="btn-primary flex items-center gap-2"
          >
            <UsersIcon size={16} />
            Add User
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-4">
              <div className="h-4 bg-slate-700 rounded w-1/4 mb-2" />
              <div className="h-3 bg-slate-700 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-800/50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase">User</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Role</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Department</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase">District</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Status</th>
                {isAdmin && (
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Actions</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {users?.map((user) => (
                <tr key={user.id} className="hover:bg-slate-800/30">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
                        <span className="text-sm font-medium text-slate-300">
                          {(user.full_name || user.email)[0].toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-200">{user.full_name || 'Unnamed'}</p>
                        <p className="text-xs text-slate-500 flex items-center gap-1">
                          <Mail size={10} /> {user.email}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${roleColors[user.role]}`}>
                      {roleIcons[user.role]}
                      {user.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-slate-300 flex items-center gap-1">
                      <Building size={12} className="text-slate-500" />
                      {user.department || 'NREDCAP'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-slate-400">{user.district || '-'}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                      user.is_active
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-red-500/20 text-red-400'
                    }`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  {isAdmin && (
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setEditingUser(user)}
                          className="p-1.5 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-slate-200"
                          title="Edit user"
                        >
                          <Edit2 size={16} />
                        </button>
                        {user.is_active ? (
                          <button
                            onClick={() => handleDeactivate(user)}
                            disabled={deactivatingId === user.id}
                            className="p-1.5 rounded-lg hover:bg-red-500/20 text-slate-400 hover:text-red-400 disabled:opacity-50"
                            title="Deactivate user"
                          >
                            {deactivatingId === user.id ? (
                              <Loader2 size={16} className="animate-spin" />
                            ) : (
                              <UserX size={16} />
                            )}
                          </button>
                        ) : (
                          <button
                            onClick={() => handleReactivate(user)}
                            disabled={reactivatingId === user.id}
                            className="p-1.5 rounded-lg hover:bg-green-500/20 text-slate-400 hover:text-green-400 disabled:opacity-50"
                            title="Reactivate user"
                          >
                            {reactivatingId === user.id ? (
                              <Loader2 size={16} className="animate-spin" />
                            ) : (
                              <UserCheck size={16} />
                            )}
                          </button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          {(!users || users.length === 0) && (
            <div className="p-8 text-center text-slate-500">
              No users found
            </div>
          )}
        </div>
      )}

      <UserFormModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        mode="create"
        onSubmit={handleCreateSubmit}
        isLoading={createMutation.isPending}
      />

      <UserFormModal
        isOpen={!!editingUser}
        onClose={() => setEditingUser(null)}
        mode="edit"
        userData={editingUser}
        onSubmit={handleEditSubmit}
        isLoading={updateMutation.isPending}
      />
    </div>
  );
}
