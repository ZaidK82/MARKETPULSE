import { apiClient } from "./client";

export async function getAlertRules(activeOnly = false) {
  const response = await apiClient.get("/api/v1/alert-rules", {
    params: {
      active_only: activeOnly,
    },
  });

  return response.data;
}

export async function getAlertRuleById(ruleId) {
  const response = await apiClient.get(`/api/v1/alert-rules/${ruleId}`);
  return response.data;
}

export async function createAlertRule(payload) {
  const response = await apiClient.post("/api/v1/alert-rules", payload);
  return response.data;
}

export async function updateAlertRule(ruleId, payload) {
  const response = await apiClient.patch(
    `/api/v1/alert-rules/${ruleId}`,
    payload
  );

  return response.data;
}

export async function deleteAlertRule(ruleId) {
  const response = await apiClient.delete(`/api/v1/alert-rules/${ruleId}`);
  return response.data;
}