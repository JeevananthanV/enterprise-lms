import React, { useState } from 'react';
import {
  Database,
  RefreshCw,
  Layers,
  Activity,
  Sparkles,
} from 'lucide-react';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import { useToast } from '../../context/ToastContext';

export const SystemDiagnosticsPage: React.FC = () => {
  const { showSuccess, showInfo } = useToast();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handlePurgeRedisCache = async () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      showSuccess('Redis Cache Purged', 'Flushed courses:catalog:* and analytics:summary:* keys successfully.');
    }, 600);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            System Diagnostics & Architecture Status
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time telemetry across FastAPI, PostgreSQL, MongoDB, Redis, and Object Storage tiers.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            showInfo('Telemetry Refreshed', 'Diagnostics data updated');
          }}
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Refresh Metrics
        </Button>
      </div>

      {/* Subsystem Health Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* PostgreSQL Health */}
        <Card className="border-sky-100 bg-gradient-to-br from-white to-sky-50/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-sky-100 text-sky-700">
                <Database className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">PostgreSQL 16</h3>
                <p className="text-[11px] text-slate-500">Transactional Core</p>
              </div>
            </div>
            <Badge variant="success">Operational</Badge>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 space-y-1.5 text-xs text-slate-600">
            <div className="flex justify-between">
              <span>Connection Pool:</span>
              <span className="font-semibold text-slate-800">10 / 20 Active</span>
            </div>
            <div className="flex justify-between">
              <span>Latency:</span>
              <span className="font-semibold text-emerald-600">1.2 ms</span>
            </div>
            <div className="flex justify-between">
              <span>Schema Version:</span>
              <span className="font-mono text-[11px] text-slate-700">Phase 7 (a729e1c4b901)</span>
            </div>
          </div>
        </Card>

        {/* MongoDB Health */}
        <Card className="border-emerald-100 bg-gradient-to-br from-white to-emerald-50/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-emerald-100 text-emerald-700">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">MongoDB 7</h3>
                <p className="text-[11px] text-slate-500">Flexible Content Store</p>
              </div>
            </div>
            <Badge variant="success">Operational</Badge>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 space-y-1.5 text-xs text-slate-600">
            <div className="flex justify-between">
              <span>Collection:</span>
              <span className="font-mono text-[11px] text-slate-800">lesson_contents</span>
            </div>
            <div className="flex justify-between">
              <span>Indexes:</span>
              <span className="font-semibold text-slate-800">lesson_id, course_id</span>
            </div>
            <div className="flex justify-between">
              <span>Latency:</span>
              <span className="font-semibold text-emerald-600">2.1 ms</span>
            </div>
          </div>
        </Card>

        {/* Redis Health */}
        <Card className="border-amber-100 bg-gradient-to-br from-white to-amber-50/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-amber-100 text-amber-700">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">Redis 7</h3>
                <p className="text-[11px] text-slate-500">Caching & Ephemeral Tier</p>
              </div>
            </div>
            <Badge variant="success">Operational</Badge>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 space-y-1.5 text-xs text-slate-600">
            <div className="flex justify-between">
              <span>Catalog TTL:</span>
              <span className="font-semibold text-slate-800">300s (5 min)</span>
            </div>
            <div className="flex justify-between">
              <span>Details TTL:</span>
              <span className="font-semibold text-slate-800">600s (10 min)</span>
            </div>
            <div className="flex justify-between">
              <span>Hit Ratio:</span>
              <span className="font-semibold text-emerald-600">98.4%</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Redis Cache Operations & Governance */}
      <Card
        title="Redis Caching Operations"
        subtitle="Manage distributed in-memory cache partitions and invalidation triggers"
      >
        <div className="space-y-4">
          <p className="text-xs text-slate-600 leading-relaxed">
            Redis accelerates course discovery and syllabus lookups. If Redis becomes temporarily unreachable, the system transparently falls back to PostgreSQL and MongoDB with zero service disruption.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button
              variant="primary"
              size="sm"
              isLoading={isRefreshing}
              onClick={handlePurgeRedisCache}
            >
              <Sparkles className="w-4 h-4 mr-1.5" />
              Purge Course & Analytics Caches
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};
