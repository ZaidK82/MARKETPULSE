export default function StatCard({
  label,
  value,
  helper,
  loading = false,
  error = false,
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>

      {loading ? (
        <p className="mt-3 text-sm text-slate-500">Loading...</p>
      ) : error ? (
        <p className="mt-3 text-sm font-medium text-red-600">{error}</p>
      ) : (
        <p className="mt-3 text-2xl font-bold">{value}</p>
      )}

      {helper && !loading && !error && (
        <p className="mt-2 text-xs text-slate-500">{helper}</p>
      )}
    </div>
  );
}