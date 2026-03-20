import { useState, useEffect } from 'react';
import { X, Loader2 } from 'lucide-react';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'officer' | 'developer';
  department: string;
  district?: string;
  is_active: boolean;
}

interface UserFormData {
  email: string;
  password: string;
  full_name: string;
  role: 'admin' | 'officer' | 'developer';
  department: string;
  district: string;
}

interface UserFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode: 'create' | 'edit';
  userData?: User | null;
  onSubmit: (data: UserFormData) => Promise<void>;
  isLoading?: boolean;
}

const initialFormData: UserFormData = {
  email: '',
  password: '',
  full_name: '',
  role: 'developer',
  department: '',
  district: '',
};

export default function UserFormModal({
  isOpen,
  onClose,
  mode,
  userData,
  onSubmit,
  isLoading = false,
}: UserFormModalProps) {
  const [formData, setFormData] = useState<UserFormData>(initialFormData);
  const [errors, setErrors] = useState<Partial<Record<keyof UserFormData, string>>>({});

  useEffect(() => {
    if (isOpen && mode === 'edit' && userData) {
      setFormData({
        email: userData.email,
        password: '',
        full_name: userData.full_name || '',
        role: userData.role,
        department: userData.department || '',
        district: userData.district || '',
      });
    } else if (isOpen && mode === 'create') {
      setFormData(initialFormData);
    }
    setErrors({});
  }, [isOpen, mode, userData]);

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof UserFormData, string>> = {};

    if (mode === 'create') {
      if (!formData.email.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        newErrors.email = 'Invalid email format';
      }

      if (!formData.password.trim()) {
        newErrors.password = 'Password is required';
      } else if (formData.password.length < 6) {
        newErrors.password = 'Password must be at least 6 characters';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    await onSubmit(formData);
  };

  const handleChange = (field: keyof UserFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/60" onClick={onClose} />
      <div className="relative bg-slate-900 rounded-xl shadow-xl w-full max-w-md mx-4 border border-slate-800">
        <div className="flex items-center justify-between p-4 border-b border-slate-800">
          <h2 className="text-lg font-semibold text-slate-100">
            {mode === 'create' ? 'Add New User' : 'Edit User'}
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {mode === 'create' && (
            <>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  Email <span className="text-red-400">*</span>
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  className={`w-full px-3 py-2 rounded-lg bg-slate-800 border ${
                    errors.email ? 'border-red-500' : 'border-slate-700'
                  } text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                  placeholder="user@example.com"
                  disabled={isLoading}
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-400">{errors.email}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  Password <span className="text-red-400">*</span>
                </label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => handleChange('password', e.target.value)}
                  className={`w-full px-3 py-2 rounded-lg bg-slate-800 border ${
                    errors.password ? 'border-red-500' : 'border-slate-700'
                  } text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                  placeholder="Min 6 characters"
                  disabled={isLoading}
                />
                {errors.password && (
                  <p className="mt-1 text-sm text-red-400">{errors.password}</p>
                )}
              </div>
            </>
          )}

          {mode === 'edit' && userData && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
              <input
                type="email"
                value={userData.email}
                disabled
                className="w-full px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700 text-slate-400 cursor-not-allowed"
              />
              <p className="mt-1 text-xs text-slate-500">Email cannot be changed</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Full Name</label>
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) => handleChange('full_name', e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="John Doe"
              disabled={isLoading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Role <span className="text-red-400">*</span>
            </label>
            <select
              value={formData.role}
              onChange={(e) => handleChange('role', e.target.value as UserFormData['role'])}
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            >
              <option value="developer">Developer</option>
              <option value="officer">Officer</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Department</label>
            <input
              type="text"
              value={formData.department}
              onChange={(e) => handleChange('department', e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="NREDCAP"
              disabled={isLoading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">District</label>
            <select
              value={formData.district}
              onChange={(e) => handleChange('district', e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            >
              <option value="">Select District</option>
              <option value="Anantapur">Anantapur</option>
              <option value="Chittoor">Chittoor</option>
              <option value="East Godavari">East Godavari</option>
              <option value="Guntur">Guntur</option>
              <option value="Kadapa">Kadapa</option>
              <option value="Krishna">Krishna</option>
              <option value="Kurnool">Kurnool</option>
              <option value="Nellore">Nellore</option>
              <option value="Prakasam">Prakasam</option>
              <option value="Srikakulam">Srikakulam</option>
              <option value="Visakhapatnam">Visakhapatnam</option>
              <option value="Vizianagaram">Vizianagaram</option>
              <option value="West Godavari">West Godavari</option>
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading && <Loader2 size={16} className="animate-spin" />}
              {mode === 'create' ? 'Create User' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
