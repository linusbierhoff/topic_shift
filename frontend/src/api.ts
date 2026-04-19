import axios from "axios";
import type { FullTaskModel, ResultModel, Status } from "./models";

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || "http://localhost:8000/api"),
});

export const startTask = async (
  file: File,
  theme: string,
  remove_substrings: string[] = [],
  clusters: number | null = null,
  window_size: number | null = null,
): Promise<{ task_id: number; status: Status }> => {
  const formData = new FormData();
  formData.append("file", file);

  const params = new URLSearchParams();
  params.append("theme", theme);
  remove_substrings.forEach((s) => params.append("remove_substrings", s));
  if (clusters !== null && clusters.toString() !== "") {
    params.append("clusters", clusters.toString());
  }
  if (window_size !== null && window_size.toString() !== "") {
    params.append("window_size", window_size.toString());
  }

  const response = await api.post<{ task_id: number; status: Status }>(
    `/task/start?${params.toString()}`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  );
  return response.data;
};

export const getResult = async (taskId: number): Promise<ResultModel | null> => {
  const response = await api.get<ResultModel | null>(`/task/${taskId}/result`);
  return response.data;
};

export const getAllTasks = async (): Promise<FullTaskModel[]> => {
  const response = await api.get<FullTaskModel[]>("/tasks");
  return response.data;
};

export const deleteTask = async (taskId: number): Promise<{ message: string }> => {
  const response = await api.delete<{ message: string }>(`/task/${taskId}`);
  return response.data;
};
