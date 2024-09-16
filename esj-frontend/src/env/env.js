"use server";
export const getEnv = async () => ({
    SPRINGBOOT_API_URL: process.env.NEXT_PUBLIC_SPRINGBOOT_API_URL,
    SPRING_SOCKET: process.env.NEXT_PUBLIC_SPRING_SOCKET,
    FLASK_API_URL: process.env.NEXT_PUBLIC_FLASK_API_URL,
    EXPRESS_API_URL: process.env.NEXT_PUBLIC_EXPRESS_API_URL,
});
