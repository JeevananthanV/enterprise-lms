import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Shield, Lock, Mail, AlertCircle, Sparkles } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';

export const LoginPage: React.FC = () => {
  const { login, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Redirect if already logged in
  React.useEffect(() => {
    if (isAuthenticated && user) {
      if (user.role === 'PLATFORM_ADMIN') navigate('/admin/dashboard', { replace: true });
      else if (user.role === 'INSTRUCTOR') navigate('/instructor/dashboard', { replace: true });
      else navigate('/student/dashboard', { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setIsLoading(true);

    try {
      const res = await login({ email, password });
      const from = (location.state as any)?.from?.pathname;
      if (from) {
        navigate(from, { replace: true });
      } else if (res.user.role === 'PLATFORM_ADMIN') {
        navigate('/admin/dashboard', { replace: true });
      } else if (res.user.role === 'INSTRUCTOR') {
        navigate('/instructor/dashboard', { replace: true });
      } else {
        navigate('/student/dashboard', { replace: true });
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword('');
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-sky-600 text-white font-bold shadow-lg mb-3">
          <Shield className="w-7 h-7" />
        </div>
        <h2 className="text-2xl font-extrabold text-white tracking-tight">
          Enterprise <span className="text-sky-400">LMS</span>
        </h2>
        <p className="mt-1 text-xs text-slate-400">
          Zero-Trust Role-Based Authentication Portal
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <Card className="bg-white/95 backdrop-blur shadow-2xl border-slate-700">
          {errorMsg && (
            <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@enterprise.com"
                  className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all"
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full py-2.5 text-xs font-semibold mt-2"
              isLoading={isLoading}
            >
              Sign In to LMS
            </Button>
          </form>

          {/* Quick-Fill Role Email Box */}
          <div className="mt-6 pt-5 border-t border-slate-100">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 mb-1">
              <Sparkles className="w-3.5 h-3.5 text-sky-500" />
              <span>Quick Role Email Prefill:</span>
            </div>
            <p className="text-[11px] text-slate-500 mb-2.5">
              Select an account email, then enter your configured credentials from <code className="bg-slate-100 px-1 rounded text-sky-700">.env</code>:
            </p>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('student@lms.enterprise.local')}
                className="p-2 rounded-lg border border-slate-200 bg-slate-50 hover:bg-sky-50 hover:border-sky-300 text-[11px] font-medium text-slate-700 text-center transition-all"
              >
                Student
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('instructor@lms.enterprise.local')}
                className="p-2 rounded-lg border border-slate-200 bg-slate-50 hover:bg-amber-50 hover:border-amber-300 text-[11px] font-medium text-slate-700 text-center transition-all"
              >
                Instructor
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('admin@lms.enterprise.local')}
                className="p-2 rounded-lg border border-slate-200 bg-slate-50 hover:bg-rose-50 hover:border-rose-300 text-[11px] font-medium text-slate-700 text-center transition-all"
              >
                Admin
              </button>
            </div>
          </div>

          <div className="mt-5 text-center">
            <p className="text-xs text-slate-500">
              Don't have an account?{' '}
              <Link to="/register" className="font-semibold text-sky-600 hover:text-sky-700">
                Register here
              </Link>
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};
