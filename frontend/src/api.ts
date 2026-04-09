import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api", // assuming backend runs on port 8000
});

export const startTask = async (
  file: File,
  theme: string,
  remove_substrings: string[] = [],
  clusters: number | null = null,
) => {
  const formData = new FormData();
  formData.append("file", file);

  const params = new URLSearchParams();
  params.append("theme", theme);
  remove_substrings.forEach((s) => params.append("remove_substrings", s));
  if (clusters !== null && clusters.toString() !== "") {
    params.append("clusters", clusters.toString());
  }

  const response = await api.post(
    `/task/start?${params.toString()}`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  );
  return response.data; // returns { task_id, status }
};

export const getResult = async (taskId: number) => {
  const response = await api.get(`/task/${taskId}/result`);
  return response.data; // returns ResultModel
};

export const getAllTasks = async () => {
  const response = await api.get("/tasks");
  return response.data;
};

export const deleteTask = async (taskId: number) => {
  const response = await api.delete(`/task/${taskId}`);
  return response.data;
};
