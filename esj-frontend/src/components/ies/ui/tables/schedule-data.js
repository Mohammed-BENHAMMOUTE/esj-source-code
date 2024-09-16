"use client"
import axios from "axios";

export function DATA(token, id, env) {
  const fetch1 = async () => {
    const data = await axios(`${env.SPRINGBOOT_API_URL}/responsables/${id}/streams?phase=goingto`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    const noanimated = data.data;
    return noanimated;
  }
  const fetch2 = async () => {
    const data = await axios(`${env.SPRINGBOOT_API_URL}/responsables/${id}/streams?phase=animated`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    const animated = data.data;
    return animated;
  }
  return {
    fetch1,
    fetch2
  }


}




