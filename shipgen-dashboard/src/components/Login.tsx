import React, { useState } from 'react';
import { Lock, Mail, ChevronRight, ShieldCheck, Eye, EyeOff } from 'lucide-react';
import Footer from './Footer';
import { useLocation, useNavigate } from 'react-router-dom';
import { login } from '../services/auth';
import { PH } from '../constants/formPlaceholders';

interface LoginProps {
  onLogin: (user: { id: string; email: string; name: string; role: string; companyId: string }) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [identity, setIdentity] = useState('admin@techliv.net');
  const [password, setPassword] = useState('admin123');
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
        role: 'SUPER_ADMIN',
        companyId: 'default',
      };
      localStorage.setItem('user', JSON.stringify(appUser));
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
          <div className="mb-6 rounded-xl border border-blue-100 bg-blue-50 p-4">
            <h3 className="text-sm font-bold text-blue-900">Demo Credentials</h3>
            <p className="text-sm text-blue-800 mt-1">admin@techliv.net / admin123</p>
            <p className="text-sm text-blue-800">user@techliv.net / user123</p>
          </div>
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
