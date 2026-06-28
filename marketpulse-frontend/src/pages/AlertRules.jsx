import { useEffect, useMemo, useState } from "react";
import {
  createAlertRule,
  deleteAlertRule,
  getAlertRules,
  updateAlertRule,
} from "../api/alertRulesApi";
import { evaluateAlertRule } from "../api/evaluationApi";
import { getStocks } from "../api/stocksApi";

const indicators = [
  "close_price",
  "sma",
  "ema",
  "rsi",
  "macd",
  "macd_signal",
  "macd_histogram",
];

const operators = [">", ">=", "<", "<=", "==", "!="];

const directions = ["bullish", "bearish"];

const timeframes = ["1d", "1h", "15m", "5m"];

const initialForm = {
  stock_id: "",
  name: "",
  indicator: "close_price",
  operator: ">",
  target_value: "",
  direction: "bullish",
  timeframe: "1d",
};

function normalizeList(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

export default function AlertRules() {
  const [stocks, setStocks] = useState([]);
  const [rules, setRules] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [editingRuleId, setEditingRuleId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [evaluationResult, setEvaluationResult] = useState(null);

  const stockById = useMemo(() => {
    const map = new Map();

    stocks.forEach((stock) => {
      map.set(stock.id, stock);
    });

    return map;
  }, [stocks]);

  async function loadData() {
    setLoading(true);
    setError("");

    try {
      const [stocksData, rulesData] = await Promise.all([
        getStocks(),
        getAlertRules(false),
      ]);

      setStocks(normalizeList(stocksData));
      setRules(normalizeList(rulesData));
    } catch (err) {
      setError(err.message || "Unable to load alert rules.");
    } finally {
      setLoading(false);
    }
  }

  function resetForm() {
    setForm(initialForm);
    setEditingRuleId(null);
  }

  function handleEdit(rule) {
    setEditingRuleId(rule.id);

    setForm({
      stock_id: String(rule.stock_id),
      name: rule.name || "",
      indicator: rule.indicator || "close_price",
      operator: rule.operator || ">",
      target_value:
        rule.target_value === null || rule.target_value === undefined
          ? ""
          : String(rule.target_value),
      direction: rule.direction || "bullish",
      timeframe: rule.timeframe || "1d",
      is_active: Boolean(rule.is_active),
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!form.stock_id) {
      setError("Select a stock before creating an alert rule.");
      return;
    }

    if (!form.name.trim()) {
      setError("Enter an alert rule name.");
      return;
    }

    if (form.target_value === "") {
      setError("Enter a target value.");
      return;
    }

    setActionLoading(true);
    setError("");
    setEvaluationResult(null);

    try {
      if (editingRuleId) {
        await updateAlertRule(editingRuleId, {
          name: form.name.trim(),
          indicator: form.indicator,
          operator: form.operator,
          target_value: Number(form.target_value),
          direction: form.direction,
          timeframe: form.timeframe,
          is_active: Boolean(form.is_active),
        });
      } else {
        await createAlertRule({
          stock_id: Number(form.stock_id),
          name: form.name.trim(),
          indicator: form.indicator,
          operator: form.operator,
          target_value: Number(form.target_value),
          direction: form.direction,
          timeframe: form.timeframe,
        });
      }

      resetForm();
      await loadData();
    } catch (err) {
      setError(err.message || "Unable to save alert rule.");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleToggleActive(rule) {
    setActionLoading(true);
    setError("");

    try {
      await updateAlertRule(rule.id, {
        name: rule.name,
        indicator: rule.indicator,
        operator: rule.operator,
        target_value: Number(rule.target_value),
        direction: rule.direction,
        timeframe: rule.timeframe,
        is_active: !rule.is_active,
      });

      await loadData();
    } catch (err) {
      setError(err.message || "Unable to update alert rule status.");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleDelete(ruleId) {
    setActionLoading(true);
    setError("");
    setEvaluationResult(null);

    try {
      await deleteAlertRule(ruleId);
      await loadData();
    } catch (err) {
      setError(err.message || "Unable to delete alert rule.");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleEvaluate(ruleId) {
    setActionLoading(true);
    setError("");
    setEvaluationResult(null);

    try {
      const result = await evaluateAlertRule(ruleId);
      setEvaluationResult(result);
      await loadData();
    } catch (err) {
      setError(err.message || "Unable to evaluate alert rule.");
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
          <h1 className="text-3xl font-bold">Alert Rules</h1>
          <p className="mt-2 text-slate-600">
            Create, manage, and manually evaluate stock alert rules.
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

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold">
          {editingRuleId ? "Edit Alert Rule" : "Create Alert Rule"}
        </h2>
        <p className="mt-1 text-sm text-slate-600">
          Define a price or indicator condition that can trigger an alert event.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 grid gap-4 xl:grid-cols-3">
          <div>
            <label className="text-sm font-medium text-slate-700">Stock</label>
            <select
              value={form.stock_id}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  stock_id: event.target.value,
                }))
              }
              disabled={Boolean(editingRuleId)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900 disabled:bg-slate-100"
              required
            >
              <option value="">Select stock</option>
              {stocks.map((stock) => (
                <option key={stock.id} value={stock.id}>
                  {stock.symbol} — {stock.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">
              Rule Name
            </label>
            <input
              value={form.name}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  name: event.target.value,
                }))
              }
              placeholder="AAPL RSI above 70"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">
              Indicator
            </label>
            <select
              value={form.indicator}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  indicator: event.target.value,
                }))
              }
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
            >
              {indicators.map((indicator) => (
                <option key={indicator} value={indicator}>
                  {indicator}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">
              Operator
            </label>
            <select
              value={form.operator}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  operator: event.target.value,
                }))
              }
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
            >
              {operators.map((operator) => (
                <option key={operator} value={operator}>
                  {operator}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">
              Target Value
            </label>
            <input
              type="number"
              step="0.01"
              value={form.target_value}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  target_value: event.target.value,
                }))
              }
              placeholder="150"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">
              Direction
            </label>
            <select
              value={form.direction}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  direction: event.target.value,
                }))
              }
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
            >
              {directions.map((direction) => (
                <option key={direction} value={direction}>
                  {direction}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">
              Timeframe
            </label>
            <select
              value={form.timeframe}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  timeframe: event.target.value,
                }))
              }
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
            >
              {timeframes.map((timeframe) => (
                <option key={timeframe} value={timeframe}>
                  {timeframe}
                </option>
              ))}
            </select>
          </div>

          {editingRuleId && (
            <div>
              <label className="text-sm font-medium text-slate-700">
                Status
              </label>
              <select
                value={form.is_active ? "active" : "inactive"}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    is_active: event.target.value === "active",
                  }))
                }
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          )}

          <div className="flex items-end gap-3">
            <button
              type="submit"
              disabled={actionLoading}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {actionLoading
                ? "Saving..."
                : editingRuleId
                  ? "Update Rule"
                  : "Create Rule"}
            </button>

            {editingRuleId && (
              <button
                type="button"
                onClick={resetForm}
                className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </section>

      {evaluationResult && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Latest Evaluation Result</h2>
          <pre className="mt-4 max-h-80 overflow-auto rounded-xl bg-slate-900 p-4 text-sm text-slate-100">
            {JSON.stringify(evaluationResult, null, 2)}
          </pre>
        </section>
      )}

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-6">
          <div>
            <h2 className="text-xl font-semibold">Configured Rules</h2>
            <p className="mt-1 text-sm text-slate-600">
              Existing alert rules stored in the backend.
            </p>
          </div>

          <p className="rounded-full border border-slate-200 px-3 py-1 text-sm text-slate-600">
            {rules.length} total
          </p>
        </div>

        <div className="mt-6 overflow-hidden rounded-xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Stock</th>
                <th className="px-4 py-3 font-medium">Condition</th>
                <th className="px-4 py-3 font-medium">Direction</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-200">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-4 py-6 text-slate-500">
                    Loading alert rules...
                  </td>
                </tr>
              ) : rules.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-4 py-6 text-slate-500">
                    No alert rules created yet.
                  </td>
                </tr>
              ) : (
                rules.map((rule) => {
                  const stock = stockById.get(rule.stock_id);

                  return (
                    <tr key={rule.id}>
                      <td className="px-4 py-3 text-slate-500">{rule.id}</td>
                      <td className="px-4 py-3 font-medium">{rule.name}</td>
                      <td className="px-4 py-3">
                        {stock?.symbol || `Stock #${rule.stock_id}`}
                      </td>
                      <td className="px-4 py-3">
                        <span className="font-mono text-xs">
                          {rule.indicator} {rule.operator} {rule.target_value}
                        </span>
                      </td>
                      <td className="px-4 py-3">{rule.direction}</td>
                      <td className="px-4 py-3">
                        <span
                          className={[
                            "rounded-full px-2 py-1 text-xs font-medium",
                            rule.is_active
                              ? "bg-green-50 text-green-700"
                              : "bg-slate-100 text-slate-600",
                          ].join(" ")}
                        >
                          {rule.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-2">
                          <button
                            onClick={() => handleEvaluate(rule.id)}
                            disabled={actionLoading || !rule.is_active}
                            className="rounded-lg border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                          >
                            Evaluate
                          </button>

                          <button
                            onClick={() => handleEdit(rule)}
                            disabled={actionLoading}
                            className="rounded-lg border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                          >
                            Edit
                          </button>

                          <button
                            onClick={() => handleToggleActive(rule)}
                            disabled={actionLoading}
                            className="rounded-lg border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                          >
                            {rule.is_active ? "Disable" : "Enable"}
                          </button>

                          <button
                            onClick={() => handleDelete(rule.id)}
                            disabled={actionLoading}
                            className="rounded-lg border border-red-200 px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}