import React from 'react';
import { useNavigate } from 'react-router-dom';
import { EmptyState } from '../components/common/EmptyState';
import { Card } from '../components/common/Card';
import { FileQuestion } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="py-12">
      <Card className="max-w-xl mx-auto">
        <EmptyState
          icon={<FileQuestion className="w-10 h-10 text-slate-400" />}
          title="Page Not Found"
          description="The resource or route you are attempting to access does not exist in the Enterprise LMS."
          actionText="Back to Dashboard"
          onAction={() => navigate('/')}
        />
      </Card>
    </div>
  );
};
