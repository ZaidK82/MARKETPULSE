import { Routes, Route } from "react-router-dom";
import AppLayout from "../layouts/AppLayout";
import Dashboard from "../pages/Dashboard";
import Stocks from "../pages/Stocks";
import AlertRules from "../pages/AlertRules";
import AlertHistory from "../pages/AlertHistory";
import Scheduler from "../pages/Scheduler";
import NotFound from "../pages/NotFound";

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/stocks" element={<Stocks />} />
        <Route path="/alerts" element={<AlertRules />} />
        <Route path="/history" element={<AlertHistory />} />
        <Route path="/scheduler" element={<Scheduler />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}