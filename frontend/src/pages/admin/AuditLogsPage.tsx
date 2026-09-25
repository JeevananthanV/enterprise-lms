import React, { useState } from 'react';
import {
  Search,
  Lock,
  Clock,
  User,
} from 'lucide-react';
import { Badge } from '../../components/common/Badge';
import { Tabs } from '../../components/common/Tabs';

interface AuditEvent {
  id: string;
  actor: string;
  action: string;
  resource: string;
  timestamp: string;
  status: 'SUCCESS' | 'WARNING' | 'FAILED';
  ip_address: string;
  details: string;
}

export const AuditLogsPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const auditEvents: AuditEvent[] = [
    {
      id: 'evt-001',
      actor: 'admin@example.com',
      action: 'ROLE_ELEVATION',
      resource: 'user:4',
      timestamp: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
      status: 'SUCCESS',
      ip_address: '192.168.1.100',
      details: 'Elevated user permissions to INSTRUCTOR',
    },
    {
      id: 'evt-002',
      actor: 'instructor.alice@example.com',
      action: 'COURSE_PUBLISH',
      resource: 'course:uuid-101',
      timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
      status: 'SUCCESS',
      ip_address: '10.0.0.45',
      details: 'Published course: "Enterprise PostgreSQL Architecture"',
    },
    {
      id: 'evt-003',
      actor: 'unknown_client',
      action: 'AUTH_FAILURE',
      resource: 'auth:login',
      timestamp: new Date(Date.now() - 1000 * 60 * 110).toISOString(),
      status: 'FAILED',
      ip_address: '203.0.113.195',
      details: 'Failed password attempt for user admin@example.com (Invalid credentials)',
    },
    {
      id: 'evt-004',
      actor: 'system_cache_daemon',
      action: 'CACHE_PURGE',
      resource: 'redis:courses:catalog:*',
      timestamp: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
      status: 'SUCCESS',
      ip_address: '127.0.0.1',
      details: 'Automatic Redis cache invalidation following module creation',
    },
    {
      id: 'evt-005',
      actor: 'student.charlie@example.com',
      action: 'CERTIFICATE_GENERATION',
      resource: 'cert:CERT-2026-9481',
      timestamp: new Date(Date.now() - 1000 * 60 * 240).toISOString(),
      status: 'SUCCESS',
      ip_address: '172.16.0.8',
      details: 'Issued Certificate of Completion for course score 94.0%',
    },
  ];

  const filteredEvents = auditEvents.filter((evt) => {
    const matchesSearch =
      evt.actor.toLowerCase().includes(search.toLowerCase()) ||
      evt.action.toLowerCase().includes(search.toLowerCase()) ||
      evt.details.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || evt.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Security & Immutable Audit Trail
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Cryptographically signed, tamper-evident audit logs capturing administrative actions, authentication events, and compliance milestones.
        </p>
      </div>

      {/* Status Filter Tabs */}
      <Tabs
        tabs={[
          { id: 'ALL', label: 'All Events', count: auditEvents.length },
          { id: 'SUCCESS', label: 'Successful', count: auditEvents.filter((e) => e.status === 'SUCCESS').length },
          { id: 'FAILED', label: 'Security Alerts / Failed', count: auditEvents.filter((e) => e.status === 'FAILED').length },
        ]}
        activeTab={statusFilter}
        onChange={setStatusFilter}
      />

      {/* Search Bar */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative max-w-sm w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by actor, action, resource..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100 transition-all shadow-xs"
          />
        </div>
        <div className="flex items-center gap-1.5 text-xs text-slate-500">
          <Lock className="w-3.5 h-3.5 text-emerald-600" />
          <span>WORM Compliant Storage</span>
        </div>
      </div>

      {/* Events Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/80 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <th className="py-3.5 px-4">Event Type / Actor</th>
                <th className="py-3.5 px-4">Resource</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">IP / Timestamp</th>
                <th className="py-3.5 px-4">Audit Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {filteredEvents.map((evt) => (
                <tr key={evt.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="space-y-0.5">
                      <p className="font-bold text-slate-900 font-mono">{evt.action}</p>
                      <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
                        <User className="w-3 h-3 text-slate-400" />
                        <span>{evt.actor}</span>
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="font-mono text-[11px] bg-slate-100 px-2 py-0.5 rounded text-slate-700">
                      {evt.resource}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <Badge
                      variant={
                        evt.status === 'SUCCESS'
                          ? 'success'
                          : evt.status === 'WARNING'
                          ? 'warning'
                          : 'error'
                      }
                    >
                      {evt.status}
                    </Badge>
                  </td>
                  <td className="py-3.5 px-4 text-slate-500">
                    <p className="font-mono text-[11px]">{evt.ip_address}</p>
                    <div className="flex items-center gap-1 text-[10px] text-slate-400 mt-0.5">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(evt.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-slate-700 max-w-xs leading-relaxed">
                    {evt.details}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
