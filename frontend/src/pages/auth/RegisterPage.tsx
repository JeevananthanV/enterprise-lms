import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Lock, Mail, User, AlertCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';

export const RegisterPage: React.FC = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('STUDENT');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (password.length < 8) {
      setErrorMsg('Password must be at least 8 characters long.');
      return;
    }

    setIsLoading(true);

    try {
      const res = await register({
        email,
        password,
        full_name: fullName,
        role,
      });

      if (res.user.role === 'PLATFORM_ADMIN') {
        navigate('/admin/dashboard', { replace: true });
      } else if (res.user.role === 'INSTRUCTOR') {
        navigate('/instructor/dashboard', { replace: true });
      } else {
        navigate('/student/dashboard', { replace: true });
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Registration failed. Please verify your details.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-sky-600 text-white font-bold shadow-lg mb-3">
          <Shield className="w-7 h-7" />
        </div>
        <h2 className="text-2xl font-extrabold text-white tracking-tight">
          Create LMS Account
        </h2>
        <p className="mt-1 text-xs text-slate-400">
          Enroll as a Student, Instructor, or Platform Administrator
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
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Alex Chen"
                  className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all"
                />
              </div>
            </div>

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
                  placeholder="alex@enterprise.com"
                  className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Password (min 8 chars)
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Account Role (RBAC)
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value as UserRole)}
                className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none"
              >
                <option value="STUDENT">Student (Learner)</option>
                <option value="INSTRUCTOR">Instructor (Course Author)</option>
                <option value="PLATFORM_ADMIN">Platform Administrator</option>
              </select>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full py-2.5 text-xs font-semibold mt-2"
              isLoading={isLoading}
            >
              Complete Registration
            </Button>
          </form>

          <div className="mt-5 text-center pt-4 border-t border-slate-100">
            <p className="text-xs text-slate-500">
              Already have an account?{' '}
              <Link to="/login" className="font-semibold text-sky-600 hover:text-sky-700">
                Sign in
              </Link>
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};
