import { apiClient } from "./client";

export async function getWatchlist() {
  const response = await apiClient.get("/api/v1/watchlist");
  return response.data;
}

export async function createWatchlistItem(payload) {
  const response = await apiClient.post("/api/v1/watchlist", payload);
  return response.data;
}

export async function deleteWatchlistItem(watchlistItemId) {
  const response = await apiClient.delete(
    `/api/v1/watchlist/${watchlistItemId}`
  );
  return response.data;
}