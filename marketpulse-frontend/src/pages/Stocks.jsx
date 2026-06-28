import { useEffect, useState } from "react";
import { createStock, getStocks } from "../api/stocksApi";
import {
  createWatchlistItem,
  deleteWatchlistItem,
  getWatchlist,
} from "../api/watchlistApi";
import { getQuote } from "../api/marketDataApi";

export default function Stocks() {
  const [stocks, setStocks] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [quote, setQuote] = useState(null);

  const [stockForm, setStockForm] = useState({
    symbol: "",
    name: "",
    exchange: "",
  });

  const [watchlistForm, setWatchlistForm] = useState({
    stock_id: "",
  });

  const [quoteSymbol, setQuoteSymbol] = useState("");

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");

    try {
      const [stocksData, watchlistData] = await Promise.all([
        getStocks(),
        getWatchlist(),
      ]);

      setStocks(Array.isArray(stocksData) ? stocksData : stocksData.items || []);
      setWatchlist(
        Array.isArray(watchlistData) ? watchlistData : watchlistData.items || []
      );
    } catch (err) {
      setError(err.message || "Unable to load stocks and watchlist.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateStock(event) {
    event.preventDefault();
    setActionLoading(true);
    setError("");

    try {
      await createStock({
        symbol: stockForm.symbol.trim().toUpperCase(),
        name: stockForm.name.trim(),
        exchange: stockForm.exchange.trim().toUpperCase(),
      });

      setStockForm({
        symbol: "",
        name: "",
        exchange: "",
      });

      await loadData();
    } catch (err) {
      setError(err.message || "Unable to create stock.");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleAddToWatchlist(event) {
    event.preventDefault();

    if (!watchlistForm.stock_id) {
      setError("Select a stock before adding it to the watchlist.");
      return;
    }

    setActionLoading(true);
    setError("");

    try {
      await createWatchlistItem({
        stock_id: Number(watchlistForm.stock_id),
      });

      setWatchlistForm({
        stock_id: "",
      });

      await loadData();
    } catch (err) {
      setError(err.message || "Unable to add stock to watchlist.");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleDeleteWatchlistItem(watchlistItemId) {
    setActionLoading(true);
    setError("");

    try {
      await deleteWatchlistItem(watchlistItemId);
      await loadData();
    } catch (err) {
      setError(err.message || "Unable to delete watchlist item.");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleQuoteLookup(event) {
    event.preventDefault();

    if (!quoteSymbol.trim()) {
      setError("Enter a symbol before fetching quote data.");
      return;
    }

    setActionLoading(true);
    setError("");
    setQuote(null);

    try {
      const quoteData = await getQuote(quoteSymbol.trim().toUpperCase());
      setQuote(quoteData);
    } catch (err) {
      setError(err.message || "Unable to fetch quote.");
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
          <h1 className="text-3xl font-bold">Stocks & Watchlist</h1>
          <p className="mt-2 text-slate-600">
            Manage tracked stocks, active watchlist entries, and live quote
            lookups.
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

      <div className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Add Stock</h2>
          <p className="mt-1 text-sm text-slate-600">
            Add a stock symbol to the backend stock registry.
          </p>

          <form onSubmit={handleCreateStock} className="mt-6 space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-700">
                Symbol
              </label>
              <input
                value={stockForm.symbol}
                onChange={(event) =>
                  setStockForm((current) => ({
                    ...current,
                    symbol: event.target.value,
                  }))
                }
                placeholder="AAPL"
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700">
                Name
              </label>
              <input
                value={stockForm.name}
                onChange={(event) =>
                  setStockForm((current) => ({
                    ...current,
                    name: event.target.value,
                  }))
                }
                placeholder="Apple Inc."
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700">
                Exchange
              </label>
              <input
                value={stockForm.exchange}
                onChange={(event) =>
                  setStockForm((current) => ({
                    ...current,
                    exchange: event.target.value,
                  }))
                }
                placeholder="NASDAQ"
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
                required
              />
            </div>

            <button
              type="submit"
              disabled={actionLoading}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {actionLoading ? "Saving..." : "Add Stock"}
            </button>
          </form>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Quote Lookup</h2>
          <p className="mt-1 text-sm text-slate-600">
            Fetch live quote data from the backend yfinance integration.
          </p>

          <form onSubmit={handleQuoteLookup} className="mt-6 flex gap-3">
            <input
              value={quoteSymbol}
              onChange={(event) => setQuoteSymbol(event.target.value)}
              placeholder="AAPL"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
            />

            <button
              type="submit"
              disabled={actionLoading}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Fetch
            </button>
          </form>

          {quote && (
            <pre className="mt-6 max-h-80 overflow-auto rounded-xl bg-slate-900 p-4 text-sm text-slate-100">
              {JSON.stringify(quote, null, 2)}
            </pre>
          )}
        </section>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-6">
          <div>
            <h2 className="text-xl font-semibold">Tracked Stocks</h2>
            <p className="mt-1 text-sm text-slate-600">
              Stocks currently stored in the backend.
            </p>
          </div>

          <p className="rounded-full border border-slate-200 px-3 py-1 text-sm text-slate-600">
            {stocks.length} total
          </p>
        </div>

        <div className="mt-6 overflow-hidden rounded-xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Symbol</th>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Exchange</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-200">
              {loading ? (
                <tr>
                  <td colSpan="4" className="px-4 py-6 text-slate-500">
                    Loading stocks...
                  </td>
                </tr>
              ) : stocks.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-4 py-6 text-slate-500">
                    No stocks added yet.
                  </td>
                </tr>
              ) : (
                stocks.map((stock) => (
                  <tr key={stock.id}>
                    <td className="px-4 py-3 text-slate-500">{stock.id}</td>
                    <td className="px-4 py-3 font-semibold">
                      {stock.symbol}
                    </td>
                    <td className="px-4 py-3">{stock.name}</td>
                    <td className="px-4 py-3">{stock.exchange}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold">Watchlist</h2>
        <p className="mt-1 text-sm text-slate-600">
          Add tracked stocks to the active watchlist.
        </p>

        <form onSubmit={handleAddToWatchlist} className="mt-6 flex gap-3">
          <select
            value={watchlistForm.stock_id}
            onChange={(event) =>
              setWatchlistForm({
                stock_id: event.target.value,
              })
            }
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
          >
            <option value="">Select stock</option>
            {stocks.map((stock) => (
              <option key={stock.id} value={stock.id}>
                {stock.symbol} — {stock.name}
              </option>
            ))}
          </select>

          <button
            type="submit"
            disabled={actionLoading}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Add
          </button>
        </form>

        <div className="mt-6 overflow-hidden rounded-xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Stock ID</th>
                <th className="px-4 py-3 font-medium">Symbol</th>
                <th className="px-4 py-3 font-medium">Action</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-200">
              {loading ? (
                <tr>
                  <td colSpan="4" className="px-4 py-6 text-slate-500">
                    Loading watchlist...
                  </td>
                </tr>
              ) : watchlist.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-4 py-6 text-slate-500">
                    No watchlist items yet.
                  </td>
                </tr>
              ) : (
                watchlist.map((item) => (
                  <tr key={item.id}>
                    <td className="px-4 py-3 text-slate-500">{item.id}</td>
                    <td className="px-4 py-3">{item.stock_id}</td>
                    <td className="px-4 py-3 font-semibold">
                      {item.stock?.symbol || item.symbol || "-"}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleDeleteWatchlistItem(item.id)}
                        disabled={actionLoading}
                        className="rounded-lg border border-red-200 px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        Remove
                      </button>
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