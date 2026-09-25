import React, { useState } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Breadcrumbs } from '../common/Breadcrumbs';

export interface AppShellProps {
  children: React.ReactNode;
  systemStatus?: string;
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  systemStatus,
}) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans antialiased text-slate-800 selection:bg-sky-500 selection:text-white">
      {/* Top Navigation Bar */}
      <Header
        onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
        systemStatus={systemStatus}
      />

      <div className="flex flex-1">
        {/* Dynamic Context Sidebar */}
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        {/* Main Content Area */}
        <main className="flex-1 md:pl-64 flex flex-col min-w-0 transition-all">
          <div className="flex-1 p-4 md:p-8 max-w-7xl w-full mx-auto space-y-4">
            {/* Automatic Breadcrumbs Navigation */}
            <Breadcrumbs />
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

