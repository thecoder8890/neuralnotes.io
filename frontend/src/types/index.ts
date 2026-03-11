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

export interface DocumentSummary {
  doc_id: string;
  source_type: string;
  source_name: string;
  processed_at: string;
  status: string;
  char_count: number;
  approx_chunks: number;
  preview: string;
  file_size?: number | null;
}

export interface SupportedFormatsResponse {
  formats: string[];
  max_file_size_mb: number;
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
