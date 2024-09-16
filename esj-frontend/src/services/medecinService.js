import axios from "axios";



export const getMedecinById = async (token, id, env) => {
  try {
    const response = await axios.get(`${env.SPRINGBOOT_API_URL}/medecins/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    if (response.status === 200) {
      return response.data;
    } else {
      throw new Error("Failed to fetch medecin data");
    }
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const updateMedecin = async (id, medecinData, env) => {
  try {
    const response = await axios.patch(
      `${env.SPRINGBOOT_API_URL}/medecins/${id}`,
      medecinData,
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    if (response.status === 200) {
      return response.data;
    } else {
      throw new Error("Failed to update medecin data");
    }
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const getAllMedecins = async (token, env) => {
  try {
    const response = await axios.get(`${env.SPRINGBOOT_API_URL}/medecins`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    if (response.status === 200) {
      return response.data;
    } else {
      throw new Error("Failed to fetch medecin data");
    }
  } catch (error) {
    console.error(error);
    throw error;
  }
}