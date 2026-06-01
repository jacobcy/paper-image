// Domain types aligned with backend paper_image/domain.py

export type CorpusScope = "public" | "private" | "submission";

export type EvidenceLevel =
  | "exact_duplicate"
  | "near_duplicate"
  | "partial_reuse"
  | "possible_manipulation"
  | "needs_review";

export type ReviewStatus =
  | "pending"
  | "confirmed"
  | "false_positive"
  | "needs_more_review"
  | "expert_review_requested";

export interface User {
  id: string;
  email: string;
  name: string;
  organization: string | null;
  role: "author" | "reviewer" | "admin";
  createdAt: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: "draft" | "uploading" | "processing" | "ready" | "completed";
  targetPdf: PdfFile | null;
  referencePdfs: PdfFile[];
  createdAt: string;
  updatedAt: string;
}

export interface PdfFile {
  id: string;
  filename: string;
  fileSize: number;
  role: "target" | "reference";
  source: "upload" | "pubmed";
  uploadProgress: number;
  processingStatus: "pending" | "extracting" | "completed" | "failed";
  figureCount: number | null;
  panelCount: number | null;
  uploadedAt: string;
}

export interface Figure {
  id: string;
  articleId: string;
  page: number;
  caption: string;
  imagePath: string;
  bbox: [number, number, number, number];
  panels: Panel[];
}

export interface Panel {
  id: string;
  figureId: string;
  label: string;
  imagePath: string;
  bbox: [number, number, number, number];
  confirmed: boolean;
  confidence: number;
}

export interface PanelSummary {
  targetPanelCount: number;
  referencePanelCount: number;
  confirmedCount: number;
  pendingCount: number;
}

export interface Finding {
  id: string;
  level: EvidenceLevel;
  score: number;
  algorithm: string;
  message: string;
  targetPanel: PanelRef;
  sourcePanel: PanelRef | null;
  heatmapPath: string | null;
  overlayPath: string | null;
  modelVersion: string;
  parameters: Record<string, unknown>;
  reviewStatus: ReviewStatus;
  reviewedBy: string | null;
  reviewedAt: string | null;
}

export interface PanelRef {
  panelId: string;
  figureId: string;
  articleId: string;
  imagePath: string;
  label: string;
  scope: CorpusScope;
}

export interface ScreeningReport {
  id: string;
  projectId: string;
  generatedAt: string;
  summary: ReportSummary;
  findings: Finding[];
  panelUsage: PanelUsage;
  modelVersions: ModelVersion[];
}

export interface ReportSummary {
  totalFindings: number;
  byLevel: Record<EvidenceLevel, number>;
  highestRiskLevel: EvidenceLevel;
  figuresAnalyzed: number;
  panelsAnalyzed: number;
}

export interface PanelUsage {
  targetPanels: number;
  internalReferencePanels: number;
  externalReferencePanels: number;
  pubmedReferencePanels: number;
  estimatedCost: number | null;
}

export interface ModelVersion {
  module: string;
  version: string;
  name: string;
}

export interface Annotation {
  id: string;
  findingId: string;
  status: ReviewStatus;
  note: string;
  reviewerName: string;
  createdAt: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations: Citation[];
  createdAt: string;
  tokenCount?: number;
}

export interface Citation {
  findingId: string;
  figureId: string;
  text: string;
}

export interface PubMedSearchResult {
  pmid: string;
  title: string;
  authors: string[];
  journal: string;
  year: number;
  abstract: string;
  doi: string | null;
  pmcId: string | null;
  pdfAvailable: boolean;
}
