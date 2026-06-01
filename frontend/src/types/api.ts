// API envelope and request/response types

export interface ApiResponse<T> {
  code: number;
  data: T;
  message: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface AuthResponse {
  user: import("./domain").User;
  accessToken: string;
  refreshToken: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  organization?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
}

export interface ReviewRequest {
  status: import("./domain").ReviewStatus;
  note?: string;
}

export interface AddPubMedReferenceRequest {
  pmid: string;
  title: string;
  doi: string | null;
  pmcId: string | null;
}

export interface ChatRequest {
  projectId: string;
  message: string;
  findingIds?: string[];
  sessionId: string;
}
