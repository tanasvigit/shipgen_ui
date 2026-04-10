import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Edit, Plus, Search, Trash2, Users } from 'lucide-react';
import { usersService, type UiUser } from '../../services/usersService';
import { ResponsiveTable } from '../ui/ResponsiveTable';
import { useToast } from '../ui/ToastProvider';
import Modal from '../common/Modal';
import UserForm from './forms/UserForm';
import { canDeleteUsers, getStoredUserRole } from '../../utils/roleAccess';
import { UserRole } from '../../types';
import { useLocation, useNavigate } from 'react-router-dom';

const UsersList: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const role = getStoredUserRole() ?? UserRole.VIEWER;
  const mayDeleteUsers = canDeleteUsers(role);
  const { showToast } = useToast();
  const [rows, setRows] = useState<UiUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [createRole, setCreateRole] = useState<'ADMIN' | 'OPERATIONS_MANAGER' | 'DISPATCHER' | 'DRIVER' | 'VIEWER' | undefined>(undefined);
  const [lockCreateRole, setLockCreateRole] = useState(false);

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const list = await usersService.list({ limit: 100, offset: 0 });
      setRows(list);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('create') !== '1') return;
    const roleParam = (params.get('role') || '').toUpperCase();
    const validRoles = new Set(['ADMIN', 'OPERATIONS_MANAGER', 'DISPATCHER', 'DRIVER', 'VIEWER']);
    if (validRoles.has(roleParam)) {
      setCreateRole(roleParam as 'ADMIN' | 'OPERATIONS_MANAGER' | 'DISPATCHER' | 'DRIVER' | 'VIEWER');
      setLockCreateRole(true);
    } else {
      setCreateRole(undefined);
      setLockCreateRole(false);
    }
    setIsCreateOpen(true);
    navigate('/analytics/users', { replace: true });
  }, [location.search, navigate]);

  const filtered = useMemo(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => `${r.name} ${r.email}`.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  const onDelete = async (id: string) => {
    if (!window.confirm('Delete this user?')) return;
    try {
      setError(null);
      await usersService.remove(id);
      setRows((prev) => prev.filter((u) => u.id !== id));
      showToast('User deleted', 'success');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete user');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Users</h1>
          <p className="text-sm text-gray-600 mt-1">User management</p>
        </div>
        <button
          type="button"
          onClick={() => setIsCreateOpen(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus size={16} />
          <span>Create User</span>
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search users by name or email..."
          className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          {filtered.length === 0 ? (
            <div className="p-12 text-center">
              <Users size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No users found</p>
            </div>
          ) : (
            <ResponsiveTable
              data={filtered}
              keyExtractor={(row) => row.id}
              columns={[
                {
                  key: 'name',
                  header: 'name',
                  render: (row) => <span className="text-sm font-medium text-gray-900 table-cell-ellipsis block" title={row.name || '—'}>{row.name || '—'}</span>,
                },
                {
                  key: 'email',
                  header: 'email',
                  render: (row) => <span className="text-sm text-gray-700 table-cell-ellipsis block" title={row.email || '—'}>{row.email || '—'}</span>,
                },
                {
                  key: 'role',
                  header: 'role',
                  render: (row) => <span className="text-sm text-gray-700">{row.role === 'VIEWER' ? 'Viewer (Read-only)' : (row.role || '—')}</span>,
                },
                {
                  key: 'status',
                  header: 'status',
                  render: (row) => <span className="text-sm text-gray-700">{row.status || '—'}</span>,
                },
                {
                  key: 'created_at',
                  header: 'created_at',
                  render: (row) => <span className="text-sm text-gray-700">{row.created_at ? new Date(row.created_at).toLocaleString() : '—'}</span>,
                  mobileHidden: true,
                },
                {
                  key: 'actions',
                  header: 'actions',
                  render: (row) => (
                    <div className="inline-flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedId(row.id);
                          setIsEditOpen(true);
                        }}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                      >
                        <Edit size={16} />
                      </button>
                      {mayDeleteUsers ? (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            void onDelete(row.id);
                          }}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                        >
                          <Trash2 size={16} />
                        </button>
                      ) : null}
                    </div>
                  ),
                },
              ]}
            />
          )}
        </div>
      )}

      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create User">
        <UserForm
          mode="create"
          initialRole={createRole}
          lockRole={lockCreateRole}
          onCancel={() => {
            setIsCreateOpen(false);
            setCreateRole(undefined);
            setLockCreateRole(false);
          }}
          onSuccess={async () => {
            setIsCreateOpen(false);
            setCreateRole(undefined);
            setLockCreateRole(false);
            showToast('User created successfully', 'success');
            await load();
          }}
        />
      </Modal>
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit User">
        <UserForm
          mode="edit"
          userId={selectedId ?? undefined}
          onCancel={() => setIsEditOpen(false)}
          onSuccess={async () => {
            setIsEditOpen(false);
            setSelectedId(null);
            showToast('User updated successfully', 'success');
            await load();
          }}
        />
      </Modal>
    </div>
  );
};

export default UsersList;
