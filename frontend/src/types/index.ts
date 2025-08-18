export interface GenerationRequest {
  doc_id: string;
  prompt: string;
  technology?: Technology;
}

export interface FileContent {
  name: string;
  content: string;
  type: string;
}

export interface GenerationResponse {
  project_id: string;
  files: FileContent[];
  structure: Record<string, any>;
  instructions: string;
}

export interface DocumentInfo {
  doc_id: string;
  url?: string;
  filename?: string;
  processed_at: string;
  status: string;
}

export enum Technology {
  SPRING_BOOT = "spring_boot",
  DJANGO = "django",
  REACT = "react",
  EXPRESS = "express",
  FLASK = "flask",
  NEXTJS = "nextjs"
}

export interface ApiResponse<T = any> {
  status: string;
  message?: string;
  data?: T;
}