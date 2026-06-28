import { apiClient } from "./client";

export async function getQuote(symbol) {
  const response = await apiClient.get(`/api/v1/market-data/${symbol}/quote`);
  return response.data;
}

export async function getHistory(symbol) {
  const response = await apiClient.get(`/api/v1/market-data/${symbol}/history`);
  return response.data;
}