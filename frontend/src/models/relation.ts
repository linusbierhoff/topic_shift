export const RelationshipModel = {
  EXAMPLE: "example",
  SPECIFICATION: "specification",
  ALTERNATIVE_TO: "alternative_to",
} as const;

export type RelationshipModel =
  (typeof RelationshipModel)[keyof typeof RelationshipModel];

export interface RelationModel {
  task_id: number;
  document_A: string;
  document_B: string;
  relationship: RelationshipModel;
}
