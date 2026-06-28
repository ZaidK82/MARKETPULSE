import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="mt-3 text-slate-600">Page not found.</p>

      <Link
        to="/"
        className="mt-6 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white"
      >
        Back to Dashboard
      </Link>
    </div>
  );
}