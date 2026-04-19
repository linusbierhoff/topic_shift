export const Status = {
  IN_PROGRESS: "in_progress",
  COMPLETED: "completed",
  FAILED: "failed",
} as const;

export type Status = (typeof Status)[keyof typeof Status];

export interface TaskModel {
  status: Status;
  theme: string;
}

export interface FullTaskModel {
  task_id: number;
  status: Status;
  theme: string;
}
