/// <reference types="vite/client" />

declare module 'lucide-react' {
  import * as React from 'react';
  export type LucideIcon = React.FC<
    React.SVGProps<SVGSVGElement> & {
      size?: number | string;
      strokeWidth?: number | string;
      className?: string;
    }
  >;
  export const BookOpen: LucideIcon;
  export const GraduationCap: LucideIcon;
  export const LayoutDashboard: LucideIcon;
  export const Layers: LucideIcon;
  export const User: LucideIcon;
  export const Users: LucideIcon;
  export const LogOut: LucideIcon;
  export const Shield: LucideIcon;
  export const ShieldAlert: LucideIcon;
  export const ShieldCheck: LucideIcon;
  export const AlertCircle: LucideIcon;
  export const AlertTriangle: LucideIcon;
  export const Inbox: LucideIcon;
  export const CheckCircle: LucideIcon;
  export const CheckCircle2: LucideIcon;
  export const Clock: LucideIcon;
  export const TrendingUp: LucideIcon;
  export const BarChart3: LucideIcon;
  export const Settings: LucideIcon;
  export const Search: LucideIcon;
  export const Filter: LucideIcon;
  export const Plus: LucideIcon;
  export const PlayCircle: LucideIcon;
  export const HelpCircle: LucideIcon;
  export const Award: LucideIcon;
  export const Bell: LucideIcon;
  export const Lock: LucideIcon;
  export const Mail: LucideIcon;
  export const ChevronRight: LucideIcon;
  export const FileText: LucideIcon;
  export const FileCheck: LucideIcon;
  export const FileQuestion: LucideIcon;
  export const Video: LucideIcon;
  export const Sparkles: LucideIcon;
  export const PenTool: LucideIcon;
  export const Database: LucideIcon;
  export const Server: LucideIcon;
  export const Menu: LucideIcon;
  export const RefreshCw: LucideIcon;
  export const Activity: LucideIcon;
}
