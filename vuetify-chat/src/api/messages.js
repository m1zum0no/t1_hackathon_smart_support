import { apiClient } from "./apiClient";

export const getHint = async (query) => {
  return await apiClient.post("/chat/hint/", null, { params: { query } });
};
