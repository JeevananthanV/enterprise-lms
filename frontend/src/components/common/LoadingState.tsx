import React from 'react';

export interface LoadingStateProps {
  message?: string;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading system resources...',
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-12 text-center ${className}`}>
      <div className="relative flex items-center justify-center">
        <div className="w-12 h-12 rounded-full border-4 border-slate-200 border-t-sky-600 animate-spin"></div>
      </div>
      <p className="mt-4 text-sm font-medium text-slate-600 animate-pulse">{message}</p>
    </div>
  );
};
