import React from 'react';
import { Card } from '../components/common/Card';
import { EmptyState } from '../components/common/EmptyState';
import { Layers } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export interface PlaceholderPageProps {
  title: string;
  domain: string;
  scheduledPhase: string;
  description: string;
}

export const PlaceholderPage: React.FC<PlaceholderPageProps> = ({
  title,
  domain,
  scheduledPhase,
  description,
}) => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
        <p className="text-xs text-slate-500 mt-1">Domain Boundary: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-sky-700 font-mono">{domain}</code> • Target: {scheduledPhase}</p>
      </div>

      <Card>
        <EmptyState
          icon={<Layers className="w-8 h-8 text-sky-500" />}
          title={`${title} Module Placeholder`}
          description={`${description} This domain route is scaffolded and will be activated during ${scheduledPhase}.`}
          actionText="Return to Dashboard"
          onAction={() => navigate('/')}
        />
      </Card>
    </div>
  );
};
