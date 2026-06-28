import { apiClient } from "./client";

export async function getNotificationLogs() {
  const response = await apiClient.get("/api/v1/notifications/logs");
  return response.data;
}

export async function getAlertEvents() {
  const response = await apiClient.get("/api/v1/notifications/alert-events");
  return response.data;
}

export async function sendDiscordNotification(alertEventId) {
  const response = await apiClient.post(
    `/api/v1/notifications/alert-events/${alertEventId}/discord`
  );
  return response.data;
}