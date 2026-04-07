import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api", // assuming backend runs on port 8000
});

export const startTask = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  // Optional parameters can be added here if needed, e.g. remove_substrings, clusters
  const response = await api.post("/task/start", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data; // returns { task_id, status }
};

export const getTask = async (taskId: number) => {
  const response = await api.get(`/task/${taskId}`);
  return response.data; // returns TaskModel or ResultModel
};

export const getAllTasks = async () => {
  const response = await api.get("/tasks");
  return response.data;
};

export const deleteTask = async (taskId: number) => {
  const response = await api.delete(`/task/${taskId}`);
  return response.data;
};
