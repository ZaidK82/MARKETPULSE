import { useEffect, useState } from "react";
import { getSchedulerStatus, runSchedulerOnce } from "../api/schedulerApi";

export default function Scheduler() {
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [runResult, setRunResult] = useState(null);

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadSchedulerStatus() {
    setLoading(true);
    setError("");

    try {
      const status = await getSchedulerStatus();
      setSchedulerStatus(status);
    } catch (err) {
      setError(err.message || "Unable to load scheduler status.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRunScheduler() {
    setActionLoading(true);
    setError("");
    setRunResult(null);

    try {
      const result = await runSchedulerOnce();
      setRunResult(result);
      await loadSchedulerStatus();
    } catch (err) {
      setError(err.message || "Unable to run scheduler.");
    } finally {
      setActionLoading(false);
    }
  }

  useEffect(() => {
    loadSchedulerStatus();
  }, []);

  const schedulerEnabled = Boolean(schedulerStatus?.scheduler_enabled);

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold">Scheduler</h1>
          <p className="mt-2 text-slate-600">
            Inspect scheduler configuration and manually trigger alert
            evaluation.
          </p>
        </div>

        <button
          onClick={loadSchedulerStatus}
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

      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-slate-500">
            Scheduler Status
          </p>

          {loading ? (
            <p className="mt-3 text-sm text-slate-500">Loading...</p>
          ) : (
            <p
              className={[
                "mt-3 text-2xl font-bold",
                schedulerEnabled ? "text-green-600" : "text-slate-900",
              ].join(" ")}
            >
              {schedulerEnabled ? "Enabled" : "Manual / Disabled"}
            </p>
          )}

          <p className="mt-2 text-xs text-slate-500">
            Controlled by backend environment settings.
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-slate-500">
            Interval Minutes
          </p>

          {loading ? (
            <p className="mt-3 text-sm text-slate-500">Loading...</p>
          ) : (
            <p className="mt-3 text-2xl font-bold">
              {schedulerStatus?.interval_minutes ?? "-"}
            </p>
          )}

          <p className="mt-2 text-xs text-slate-500">
            Background scheduler interval.
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Mode</p>

          {loading ? (
            <p className="mt-3 text-sm text-slate-500">Loading...</p>
          ) : (
            <p className="mt-3 text-2xl font-bold">
              {schedulerStatus?.mode || "-"}
            </p>
          )}

          <p className="mt-2 text-xs text-slate-500">
            Backend scheduler execution mode.
          </p>
        </div>
      </div>

      {!schedulerEnabled && !loading && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-800">
          <p className="font-semibold">Scheduler is currently manual/disabled.</p>
          <p className="mt-1">
            This is expected for free deployment setups where GitHub Actions
            cron calls the backend periodically instead of keeping an always-on
            background worker.
          </p>
        </div>
      )}

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-6">
          <div>
            <h2 className="text-xl font-semibold">Manual Scheduler Run</h2>
            <p className="mt-1 text-sm text-slate-600">
              Trigger one full alert evaluation cycle from the frontend.
            </p>
          </div>

          <button
            onClick={handleRunScheduler}
            disabled={actionLoading}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {actionLoading ? "Running..." : "Run Scheduler Once"}
          </button>
        </div>

        {runResult && (
          <pre className="mt-6 max-h-80 overflow-auto rounded-xl bg-slate-900 p-4 text-sm text-slate-100">
            {JSON.stringify(runResult, null, 2)}
          </pre>
        )}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold">Automation Flow</h2>
        <p className="mt-1 text-sm text-slate-600">
          MarketPulse supports both backend background scheduling and GitHub
          Actions cron-based triggering.
        </p>

        <div className="mt-6 rounded-xl bg-slate-50 p-5 font-mono text-sm text-slate-700">
          <p>GitHub Actions Cron</p>
          <p>↓</p>
          <p>POST /api/v1/scheduler/run-once</p>
          <p>↓</p>
          <p>Evaluate alert rules</p>
          <p>↓</p>
          <p>Create alert events</p>
          <p>↓</p>
          <p>Send Discord notifications</p>
          <p>↓</p>
          <p>Store notification logs</p>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold">Raw Scheduler Status</h2>

        <pre className="mt-4 max-h-80 overflow-auto rounded-xl bg-slate-900 p-4 text-sm text-slate-100">
          {JSON.stringify(schedulerStatus, null, 2)}
        </pre>
      </section>
    </div>
  );
}