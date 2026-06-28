import { NavLink, Outlet } from "react-router-dom";
import {
  Activity,
  Bell,
  Clock,
  History,
  LayoutDashboard,
  LineChart,
} from "lucide-react";

const navItems = [
  {
    label: "Dashboard",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    label: "Stocks",
    path: "/stocks",
    icon: LineChart,
  },
  {
    label: "Alert Rules",
    path: "/alerts",
    icon: Bell,
  },
  {
    label: "Alert History",
    path: "/history",
    icon: History,
  },
  {
    label: "Scheduler",
    path: "/scheduler",
    icon: Clock,
  },
];

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <aside className="fixed left-0 top-0 h-screen w-64 border-r border-slate-200 bg-white">
        <div className="flex h-16 items-center gap-3 border-b border-slate-200 px-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
            <Activity size={22} />
          </div>

          <div>
            <h1 className="text-lg font-bold">MarketPulse</h1>
            <p className="text-xs text-slate-500">Stock Alert System</p>
          </div>
        </div>

        <nav className="space-y-1 px-3 py-4">
          {navItems.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === "/"}
                className={({ isActive }) =>
                  [
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition",
                    isActive
                      ? "bg-slate-900 text-white"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
                  ].join(" ")
                }
              >
                <Icon size={18} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>
      </aside>

      <main className="ml-64 min-h-screen">
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-8">
          <div>
            <p className="text-sm text-slate-500">Frontend Dashboard</p>
            <h2 className="text-xl font-semibold">MarketPulse Control Panel</h2>
          </div>

          <div className="rounded-full border border-slate-200 px-4 py-2 text-sm text-slate-600">
            FastAPI Backend Connected
          </div>
        </header>

        <section className="p-8">
          <Outlet />
        </section>
      </main>
    </div>
  );
}