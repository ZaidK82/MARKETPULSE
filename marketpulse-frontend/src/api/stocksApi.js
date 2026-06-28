import { apiClient } from "./client";

export async function getStocks() {
  const response = await apiClient.get("/api/v1/stocks");
  return response.data;
}

export async function getStockById(stockId) {
  const response = await apiClient.get(`/api/v1/stocks/${stockId}`);
  return response.data;
}

export async function createStock(payload) {
  const response = await apiClient.post("/api/v1/stocks", payload);
  return response.data;
}