import React, { useState } from 'react';
import { Lock, Mail, ChevronRight, ShieldCheck, Eye, EyeOff } from 'lucide-react';
import Footer from './Footer';
import { useLocation, useNavigate } from 'react-router-dom';
import { login } from '../services/auth';
import { normalizeUserRole, UserRole } from '../types';
import { driversService } from '../services/driversService';
import { PH } from '../constants/formPlaceholders';

interface LoginProps {
  onLogin: (user: { id: string; email: string; name: string; role: UserRole; companyId: string }) => void;
}

/** Matches `fastapi-app/scripts/seed_rbac_demo_users.py` — same password for all. */
const DEMO_PASSWORD = 'RbacDemo123';
const DEMO_ACCOUNTS: { role: string; email: string; displayLabel?: string }[] = [
  { role: 'ADMIN', email: 'admin@demo.local' },
  { role: 'OPERATIONS_MANAGER', email: 'operations@demo.local' },
  { role: 'DISPATCHER', email: 'dispatcher@demo.local' },
  { role: 'DRIVER', email: 'driver@demo.local' },
  { role: 'VIEWER', email: 'viewer@demo.local', displayLabel: 'VIEWER (Read-only)' },
];

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [identity, setIdentity] = useState('admin@demo.local');
  const [password, setPassword] = useState(DEMO_PASSWORD);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();
  const location = useLocation();

  const getRedirectPath = () => {
    const params = new URLSearchParams(location.search);
    const redirect = params.get('redirect');
    return redirect ? decodeURIComponent(redirect) : '/dashboard';
  };

  const handleLogin = async () => {
    setError(null);
    setLoading(true);

    try {
      const data = await login(identity, password);
      if (!data?.token) {
        if (data?.isEnabled && data?.twoFaSession) {
          throw new Error('2FA is enabled on backend. This UI currently supports password-only login.');
        }
        throw new Error('Login failed: token not returned');
      }

      localStorage.setItem('token', data.token);
      localStorage.setItem('accessToken', data.token);

      const rawUser = data.user || {};
      const appUser = {
        id: String(rawUser.id || 'me'),
        email: rawUser.email || identity,
        name: rawUser.name || identity,
        role: normalizeUserRole(rawUser.role),
        companyId: 'default',
      };
      localStorage.setItem('user', JSON.stringify(appUser));
      
      // If user is a DRIVER, set them as online immediately after login
      if (appUser.role === UserRole.DRIVER) {
        try {
          await driversService.setOnline(true, 'active');
        } catch (err) {
          // Log error but don't block login - driver can still use the app
          console.error('Failed to set driver online status:', err);
        }
      }
      
      onLogin(appUser);
      navigate(getRedirectPath(), { replace: true });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col">
      <div className="flex-1 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center mb-4">
            <img src="/logo_logistic.png" alt="ShipGen" className="h-20 w-auto" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
            ShipGen
          </h1>
          <p className="text-gray-500 mt-2 font-medium">
            Enterprise Logistics Command
          </p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-100 p-8">
          <div className="space-y-6">
            {/* Email */}
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
                Work Email
              </label>
              <div className="relative">
                <Mail
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                  size={18}
                />
                <input
                  type="text"
                  data-testid="login-email"
                  value={identity}
                  onChange={(e) => setIdentity(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition-all text-sm"
                  placeholder="email or phone"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
                Password
              </label>
              <div className="relative">
                <Lock
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                  size={18}
                />
                <input
                  type={showPassword ? 'text' : 'password'}
                  data-testid="login-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition-all text-sm"
                  placeholder={PH.password}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <p className="text-sm text-red-600 font-medium">{error}</p>
            )}

            {/* Button */}
            <div className="pt-2">
              <button
                type="button"
                data-testid="login-submit"
                onClick={handleLogin}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-bold py-4 rounded-2xl shadow-lg shadow-blue-200 flex items-center justify-center group transition-all"
              >
                {loading ? 'Signing In...' : 'Sign In to Platform'}
                <ChevronRight
                  size={20}
                  className="ml-2 group-hover:translate-x-1 transition-transform"
                />
              </button>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-100">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-400 mb-3">
              Demo accounts · password <span className="font-mono text-gray-600 normal-case">{DEMO_PASSWORD}</span>
            </p>
            <ul className="space-y-1.5 text-xs text-gray-600">
              {DEMO_ACCOUNTS.map(({ role, email, displayLabel }) => (
                <li key={email} className="flex flex-wrap gap-x-2 gap-y-0.5">
                  <span className="font-medium text-gray-700 min-w-[8.5rem]">{displayLabel || role}</span>
                  <span className="font-mono text-gray-500">{email}</span>
                </li>
              ))}
            </ul>
            <p className="text-[11px] text-gray-400 mt-4">Also: admin@techliv.net / admin123</p>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-50 text-center">
            <p className="text-xs text-gray-400 flex items-center justify-center">
              <ShieldCheck size={14} className="mr-1 text-emerald-500" />
              SOC2 Type II & GDPR Compliant Environment
            </p>
          </div>
        </div>

        <p className="text-center mt-8 text-sm text-gray-500">Use backend credentials to sign in.</p>
      </div>
      </div>
      <Footer />
    </div>
  );
};

export default Login;
