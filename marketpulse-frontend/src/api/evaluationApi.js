import { apiClient } from "./client";

export async function evaluateAlertRule(ruleId) {
  const response = await apiClient.post(
    `/api/v1/evaluation/alert-rules/${ruleId}/evaluate`
  );
  return response.data;
}