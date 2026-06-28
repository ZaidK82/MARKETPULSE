import { apiClient } from "./client";

export async function getSma(symbol) {
  const response = await apiClient.get(`/api/v1/indicators/${symbol}/sma`);
  return response.data;
}

export async function getEma(symbol) {
  const response = await apiClient.get(`/api/v1/indicators/${symbol}/ema`);
  return response.data;
}

export async function getRsi(symbol) {
  const response = await apiClient.get(`/api/v1/indicators/${symbol}/rsi`);
  return response.data;
}

export async function getMacd(symbol) {
  const response = await apiClient.get(`/api/v1/indicators/${symbol}/macd`);
  return response.data;
}