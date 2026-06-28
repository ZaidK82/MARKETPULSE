import { useEffect, useState } from "react";
import { getHealth } from "../api/healthApi";

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadHealth() {
      try {
        const data = await getHealth();
        setHealth(data);
      } catch (err) {
        setError("Unable to connect to backend. Check if FastAPI is running.");
      }
    }

    loadHealth();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="mt-2 text-slate-600">
          Overview of stocks, alerts, scheduler status, and Discord notification flow.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Backend Status</p>

          {health ? (
            <p className="mt-3 text-2xl font-bold text-green-600">Online</p>
          ) : error ? (
            <p className="mt-3 text-sm font-medium text-red-600">{error}</p>
          ) : (
            <p className="mt-3 text-sm text-slate-500">Checking...</p>
          )}
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Stocks Tracked</p>
          <p className="mt-3 text-2xl font-bold">Coming Soon</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Active Alerts</p>
          <p className="mt-3 text-2xl font-bold">Coming Soon</p>
        </div>
      </div>

      {health && (
        <pre className="rounded-xl border border-slate-200 bg-slate-900 p-4 text-sm text-slate-100">
          {JSON.stringify(health, null, 2)}
        </pre>
      )}
    </div>
  );
}