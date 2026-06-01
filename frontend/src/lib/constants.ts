import type { EvidenceLevel } from "@/types/domain";

export const EVIDENCE_LEVEL_CONFIG: Record<
  EvidenceLevel,
  { label: string; color: string; bgColor: string }
> = {
  exact_duplicate: {
    label: "疑似完全重复",
    color: "text-red-700",
    bgColor: "bg-red-100",
  },
  near_duplicate: {
    label: "疑似近似重复",
    color: "text-orange-700",
    bgColor: "bg-orange-100",
  },
  partial_reuse: {
    label: "疑似局部复用",
    color: "text-amber-700",
    bgColor: "bg-amber-100",
  },
  possible_manipulation: {
    label: "疑似编辑痕迹",
    color: "text-purple-700",
    bgColor: "bg-purple-100",
  },
  needs_review: {
    label: "需人工确认",
    color: "text-blue-700",
    bgColor: "bg-blue-100",
  },
};

export const MAX_REFERENCE_PDFS = 5;
export const MAX_PDF_SIZE_MB = 200;
export const UPLOAD_CHUNK_SIZE = 5 * 1024 * 1024; // 5MB
