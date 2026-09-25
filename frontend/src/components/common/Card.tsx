import React, { HTMLAttributes } from 'react';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  action,
  children,
  className = '',
  ...props
}) => {
  return (
    <div
      className={`bg-white rounded-xl border border-slate-200 shadow-sm p-5 md:p-6 transition-all ${className}`}
      {...props}
    >
      {(title || subtitle || action) && (
        <div className="flex items-start justify-between mb-4 pb-3 border-b border-slate-100">
          <div>
            {title && <h3 className="text-base font-semibold text-slate-900">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
