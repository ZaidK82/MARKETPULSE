import { apiClient } from "./client";

export async function runSchedulerOnce() {
  const response = await apiClient.post("/api/v1/scheduler/run-once");
  return response.data;
}

export async function getSchedulerStatus() {
  const response = await apiClient.get("/api/v1/scheduler/status");
  return response.data;
}