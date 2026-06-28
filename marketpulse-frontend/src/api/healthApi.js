import { apiClient } from "./client";

export async function getHealth() {
  const response = await apiClient.get("/api/v1/health");
  return response.data;
}

export async function getReadiness() {
  const response = await apiClient.get("/api/v1/health/ready");
  return response.data;
}