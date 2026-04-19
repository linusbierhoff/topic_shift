import type { ClusterModel } from "./cluster";
import type { RelationModel } from "./relation";
import type { Status } from "./task";

export interface ResultModel {
  task_id: number;
  relations: RelationModel[];
  clusters: ClusterModel[];
  status?: Status;
}
