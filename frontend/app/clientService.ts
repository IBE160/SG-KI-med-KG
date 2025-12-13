// Export everything from the generated client
export * from "./openapi-client";

// Import the client configuration (interceptors, etc.)
import "@/lib/clientConfig";

// Re-export the client and SDK functions directly
// The new SDK uses simplified function names without prefixes
export {
  client,
  authJwtLogin,
  authJwtLogout,
  registerRegister,
  resetForgotPassword,
  resetResetPassword,
  verifyRequestToken,
  verifyVerify,
  usersCurrentUser,
  usersPatchCurrentUser,
  usersUser,
  usersPatchUser,
  usersDeleteUser,
  readItem,
  createItem,
  deleteItem,
  createControl,
  readControls,
  readControl,
  updateControl,
  deleteControl,
  createRisk,
  readRisks,
  readRisk,
  updateRisk,
  deleteRisk,
  createBusinessProcess,
  readBusinessProcesses,
  readBusinessProcess,
  updateBusinessProcess,
  deleteBusinessProcess,
  createRegulatoryFramework,
  readRegulatoryFrameworks,
  readRegulatoryFramework,
  updateRegulatoryFramework,
  deleteRegulatoryFramework,
  createUser,
  listUsers,
  getCurrentUser,
  updateUserRole,
  uploadDocument,
  listDocuments,
  getDocument,
  deleteDocument,
  renameDocument,
  manuallyProcessDocument,
  listSuggestions,
  updateSuggestionStatus,
  listAuditLogs,
  getDashboardMetrics,
  getPendingReviews,
  getSuggestionDetail,
  submitAssessment,
  createMapping,
  deleteMapping,
  getMappingsForControl,
  getMappingsForRequirement,
} from "./openapi-client/sdk.gen";

// Re-export commonly used types
export type {
  AuthJwtLoginError,
  AuthJwtLoginResponse,
  RegisterRegisterError,
  RegisterRegisterResponse,
  GetPendingReviewsResponse,
  GetSuggestionDetailResponse,
  SubmitAssessmentResponse,
  AssessmentAction,
  ResidualRisk,
  SuggestionDetailResponse,
  PendingReviewsResponse,
  AssessmentResponse,
  CreateMappingResponse,
  DeleteMappingResponse,
  GetMappingsForControlResponse,
  GetMappingsForRequirementResponse,
} from "./openapi-client/types.gen";

// Import assessment functions for backward compatibility aliases
import {
  getPendingReviews,
  getSuggestionDetail,
  submitAssessment,
} from "./openapi-client/sdk.gen";

// Create backward compatibility aliases for BPO assessment functions
export const assessmentsGetPendingReviews = getPendingReviews;
export const assessmentsGetSuggestionDetail = getSuggestionDetail;
export const assessmentsSubmitAssessment = submitAssessment;