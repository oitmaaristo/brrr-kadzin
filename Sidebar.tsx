import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Columns3,
  FolderOpen,
  Activity,
  BarChart3,
  Settings,
  Wifi,
  WifiOff,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/kanban", icon: Columns3, label: "Agent Board" },
  { to: "/sessions", icon: FolderOpen, label: "Sessions" },
  { to: "/activity", icon: Activity, label: "Activity Feed" },
  { to: "/analytics", icon: BarChart3, label: "Analytics" },
  { to: "/settings", icon: Settings, label: "Settings" },
] as const;

const STORAGE_KEY = "sidebar-collapsed";

function loadCollapsed(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === "true";
  } catch {
    return false;
  }
}

interface SidebarProps {
  wsConnected: boolean;
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ wsConnected, collapsed, onToggle }: SidebarProps) {
  return (
    <aside
      className={`fixed left-0 top-0 bottom-0 bg-surface-1 border-r border-border flex flex-col z-30 overflow-y-auto overflow-x-hidden transition-[width] duration-200 ${
        collapsed ? "w-[4.25rem]" : "w-60"
      }`}
    >
      {/* Brand — just the logo, nothing else */}
      <div className="px-3 py-5 border-b border-border">
        {collapsed ? (
          <div className="flex justify-center">
            <span className="text-xl font-semibold text-accent" style={{fontFamily:"Outfit"}}>b<span className="text-accent/60">.</span></span>
          </div>
        ) : (
          <div className="px-2">
            <h1 className="text-lg font-semibold text-gray-100 tracking-tight" style={{fontFamily:"Outfit"}}>brrr<span className="text-accent">.</span>kadzin</h1>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 space-y-1">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            title={collapsed ? label : undefined}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg text-sm font-medium transition-colors duration-150 ${
                collapsed ? "justify-center px-2 py-2.5" : "px-3 py-2.5"
              } ${
                isActive
                  ? "bg-accent/10 text-accent border border-accent/20"
                  : "text-gray-400 hover:text-gray-200 hover:bg-surface-3 border border-transparent"
              }`
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <div className="px-2 py-2">
        <button
          onClick={onToggle}
          className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-xs text-gray-500 hover:text-gray-300 hover:bg-surface-3 transition-colors"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <PanelLeftOpen className="w-4 h-4 flex-shrink-0 mx-auto" />
          ) : (
            <>
              <PanelLeftClose className="w-4 h-4 flex-shrink-0" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>

      {/* Footer — just connection status */}
      <div className={`px-3 py-3 border-t border-border ${collapsed ? "items-center" : ""}`}>
        <div className={`flex items-center text-xs ${collapsed ? "justify-center" : "gap-2"}`}>
          {wsConnected ? (
            <>
              <Wifi className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
              {!collapsed && <span className="text-emerald-400">Live</span>}
            </>
          ) : (
            <>
              <WifiOff className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
              {!collapsed && <span className="text-gray-500">Disconnected</span>}
            </>
          )}
        </div>
      </div>
    </aside>
  );
}

export { STORAGE_KEY as SIDEBAR_STORAGE_KEY, loadCollapsed };
