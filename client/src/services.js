import axios from 'axios';

export const askFarmAgent = async (question) => {
  try {
    const { data } = await axios.post('http://localhost:5001/api/ask', { question });
    return data.response;
  } catch (e) {
    console.error(e);
    throw e;
  }
};