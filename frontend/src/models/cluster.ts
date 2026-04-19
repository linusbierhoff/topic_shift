import type { Document } from "./document";

export interface ClusterModel {
  task_id: number;
  title: string;
  documents: Document[];
}
