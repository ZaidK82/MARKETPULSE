import { useEffect, useState } from "react";
import StatCard from "../components/StatCard";
import { getHealth, getReadiness } from "../api/healthApi";
import { getStocks } from "../api/stocksApi";
import { getWatchlist } from "../api/watchlistApi";
import { getAlertRules } from "../api/alertRulesApi";
import { getAlertEvents } from "../api/notificationsApi";
import {
  getSchedulerStatus,
  runSchedulerOnce,
} from "../api/schedulerApi";

function getCount(data) {
  if (Array.isArray(data)) return data.length;
  if (Array.isArray(data?.items)) return data.items.length;
  if (Array.isArray(data?.data)) return data.data.length;
  if (typeof data?.total === "number") return data.total;
  return 0;
}

export default function Dashboard() {
  const [dashboard, setDashboard] = useState({
    health: null,
    readiness: null,
    stocks: [],
    watchlist: [],
    alertRules: [],
    alertEvents: [],
    scheduler: null,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [schedulerLoading, setSchedulerLoading] = useState(false);
  const [schedulerResult, setSchedulerResult] = useState(null);

  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      const [
        health,
        readiness,
        stocks,
        watchlist,
        alertRules,
        alertEvents,
        scheduler,
      ] = await Promise.all([
        getHealth(),
        getReadiness(),
        getStocks(),
        getWatchlist(),
        getAlertRules(),
        getAlertEvents(),
        getSchedulerStatus(),
      ]);

      setDashboard({
        health,
        readiness,
        stocks,
        watchlist,
        alertRules,
        alertEvents,
        scheduler,
      });
    } catch (err) {
      setError(
        err.message ||
          "Unable to load dashboard data. Check if FastAPI backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleRunScheduler() {
    setSchedulerLoading(true);
    setSchedulerResult(null);

    try {
      const result = await runSchedulerOnce();
      setSchedulerResult(result);
      await loadDashboard();
    } catch (err) {
      setSchedulerResult({
        error: err.message || "Scheduler run failed.",
      });
    } finally {
      setSchedulerLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const backendOnline = dashboard.health ? "Online" : "Offline";
  const readinessStatus = dashboard.readiness ? "Ready" : "Not Ready";

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="mt-2 text-slate-600">
            Live overview of stocks, watchlist, alerts, scheduler status, and
            Discord notification flow.
          </p>
        </div>

        <button
          onClick={loadDashboard}
          disabled={loading}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700">
          {error}
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Backend Status"
          value={backendOnline}
          helper="/api/v1/health"
          loading={loading}
        />

        <StatCard
          label="Readiness"
          value={readinessStatus}
          helper="/api/v1/health/ready"
          loading={loading}
        />

        <StatCard
          label="Stocks Tracked"
          value={getCount(dashboard.stocks)}
          helper="Total stocks stored"
          loading={loading}
        />

        <StatCard
          label="Watchlist Items"
          value={getCount(dashboard.watchlist)}
          helper="Active watchlist entries"
          loading={loading}
        />

        <StatCard
          label="Alert Rules"
          value={getCount(dashboard.alertRules)}
          helper="Configured rules"
          loading={loading}
        />

        <StatCard
          label="Alert Events"
          value={getCount(dashboard.alertEvents)}
          helper="Triggered event history"
          loading={loading}
        />

        <StatCard
          label="Scheduler"
          value={dashboard.scheduler?.enabled ? "Enabled" : "Manual / Disabled"}
          helper="Scheduler lifecycle status"
          loading={loading}
        />

        <StatCard
          label="API Prefix"
          value="/api/v1"
          helper="Backend route namespace"
          loading={loading}
        />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-6">
          <div>
            <h2 className="text-xl font-semibold">Scheduler Control</h2>
            <p className="mt-1 text-sm text-slate-600">
              Manually trigger the alert evaluation workflow once.
            </p>
          </div>

          <button
            onClick={handleRunScheduler}
            disabled={schedulerLoading}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {schedulerLoading ? "Running..." : "Run Scheduler Once"}
          </button>
        </div>

        {schedulerResult && (
          <pre className="mt-6 overflow-auto rounded-xl bg-slate-900 p-4 text-sm text-slate-100">
            {JSON.stringify(schedulerResult, null, 2)}
          </pre>
        )}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold">Raw System Status</h2>
        <p className="mt-1 text-sm text-slate-600">
          Useful for debugging API responses during development.
        </p>

        <pre className="mt-6 max-h-96 overflow-auto rounded-xl bg-slate-900 p-4 text-sm text-slate-100">
          {JSON.stringify(dashboard, null, 2)}
        </pre>
      </div>
    </div>
  );
}