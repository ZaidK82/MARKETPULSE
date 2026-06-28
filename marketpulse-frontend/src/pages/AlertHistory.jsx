import { useEffect, useState } from "react";
import {
  getAlertEvents,
  getNotificationLogs,
  sendDiscordNotification,
} from "../api/notificationsApi";

function normalizeList(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function formatDate(value) {
  if (!value) return "-";

  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

export default function AlertHistory() {
  const [alertEvents, setAlertEvents] = useState([]);
  const [notificationLogs, setNotificationLogs] = useState([]);
  const [sendResult, setSendResult] = useState(null);

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");

    try {
      const [eventsData, logsData] = await Promise.all([
        getAlertEvents(),
        getNotificationLogs(),
      ]);

      setAlertEvents(normalizeList(eventsData));
      setNotificationLogs(normalizeList(logsData));
    } catch (err) {
      setError(err.message || "Unable to load alert history.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSendDiscord(alertEventId) {
    setActionLoading(true);
    setError("");
    setSendResult(null);

    try {
      const result = await sendDiscordNotification(alertEventId);
      setSendResult(result);
      await loadData();
    } catch (err) {
      setError(err.message || "Unable to send Discord notification.");
    } finally {
      setActionLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold">Alert History</h1>
          <p className="mt-2 text-slate-600">
            Review triggered alert events and Discord notification delivery logs.
          </p>
        </div>

        <button
          onClick={loadData}
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

      {sendResult && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Latest Discord Send Result</h2>
          <pre className="mt-4 max-h-80 overflow-auto rounded-xl bg-slate-900 p-4 text-sm text-slate-100">
            {JSON.stringify(sendResult, null, 2)}
          </pre>
        </section>
      )}

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-6">
          <div>
            <h2 className="text-xl font-semibold">Alert Events</h2>
            <p className="mt-1 text-sm text-slate-600">
              Events created when alert rule conditions were triggered.
            </p>
          </div>

          <p className="rounded-full border border-slate-200 px-3 py-1 text-sm text-slate-600">
            {alertEvents.length} total
          </p>
        </div>

        <div className="mt-6 overflow-hidden rounded-xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Rule ID</th>
                <th className="px-4 py-3 font-medium">Symbol</th>
                <th className="px-4 py-3 font-medium">Triggered</th>
                <th className="px-4 py-3 font-medium">Target</th>
                <th className="px-4 py-3 font-medium">Message</th>
                <th className="px-4 py-3 font-medium">Time</th>
                <th className="px-4 py-3 font-medium">Action</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-200">
              {loading ? (
                <tr>
                  <td colSpan="8" className="px-4 py-6 text-slate-500">
                    Loading alert events...
                  </td>
                </tr>
              ) : alertEvents.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-4 py-6 text-slate-500">
                    No alert events yet.
                  </td>
                </tr>
              ) : (
                alertEvents.map((event) => (
                  <tr key={event.id}>
                    <td className="px-4 py-3 text-slate-500">{event.id}</td>
                    <td className="px-4 py-3">{event.alert_rule_id}</td>
                    <td className="px-4 py-3 font-semibold">
                      {event.stock_symbol}
                    </td>
                    <td className="px-4 py-3">{event.triggered_value}</td>
                    <td className="px-4 py-3">{event.target_value}</td>
                    <td className="max-w-md px-4 py-3 text-slate-700">
                      {event.message}
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      {formatDate(event.triggered_at)}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleSendDiscord(event.id)}
                        disabled={actionLoading}
                        className="rounded-lg border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        Send Discord
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-6">
          <div>
            <h2 className="text-xl font-semibold">Notification Logs</h2>
            <p className="mt-1 text-sm text-slate-600">
              Discord notification attempts and delivery status.
            </p>
          </div>

          <p className="rounded-full border border-slate-200 px-3 py-1 text-sm text-slate-600">
            {notificationLogs.length} total
          </p>
        </div>

        <div className="mt-6 overflow-hidden rounded-xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Event ID</th>
                <th className="px-4 py-3 font-medium">Channel</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Response</th>
                <th className="px-4 py-3 font-medium">Sent At</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-200">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-4 py-6 text-slate-500">
                    Loading notification logs...
                  </td>
                </tr>
              ) : notificationLogs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-4 py-6 text-slate-500">
                    No notification logs yet.
                  </td>
                </tr>
              ) : (
                notificationLogs.map((log) => (
                  <tr key={log.id}>
                    <td className="px-4 py-3 text-slate-500">{log.id}</td>
                    <td className="px-4 py-3">{log.alert_event_id}</td>
                    <td className="px-4 py-3">{log.channel}</td>
                    <td className="px-4 py-3">
                      <span
                        className={[
                          "rounded-full px-2 py-1 text-xs font-medium",
                          log.status === "sent" || log.status === "success"
                            ? "bg-green-50 text-green-700"
                            : "bg-slate-100 text-slate-600",
                        ].join(" ")}
                      >
                        {log.status}
                      </span>
                    </td>
                    <td className="max-w-md px-4 py-3 text-slate-700">
                      {log.response_message}
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      {formatDate(log.sent_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}