import axios from "@/api/axios";

export const getHint = async (query) => {
  console.log("Sending hint request for query:", query);
  try {
    const response = await axios.post(`/chat/hint/?query=${query}`);
    console.log("Hint response received:", response.data);
    return response;
  } catch (error) {
    console.error("Error fetching hint:", error);
    throw error;
  }
};
