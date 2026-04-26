import axios from "axios";
import { useAuthStore } from "../store/authStore";

const api = axios.create({
  baseURL: "/api",
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Auth
export const login = (email: string, password: string) =>
  api.post("/auth/login", new URLSearchParams({ username: email, password }));

export const register = (email: string, password: string, fullName: string) =>
  api.post("/auth/register", { email, password, full_name: fullName });

// User
export const getProfile = () => api.get("/users/me");
export const updateProfile = (data: Record<string, unknown>) =>
  api.put("/users/me", data);

// Chat
export const sendMessage = (message: string, sessionId?: string) =>
  api.post("/chat/message", { message, session_id: sessionId });

// Plans
export const generateWorkoutPlan = (data: Record<string, unknown>) =>
  api.post("/workout/plan", data);

export const generateDietPlan = (data: Record<string, unknown>) =>
  api.post("/diet/plan", data);

// PDF Upload
export const uploadPdf = (file: File, category: string) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("category", category);
  return api.post("/chat/upload-pdf", formData);
};

export default api;
