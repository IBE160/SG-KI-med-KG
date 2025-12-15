// Export everything from the generated client
export * from "./openapi-client";

// Import the client configuration (interceptors, etc.)
import "@/lib/clientConfig";

// Re-export the SDK with all generated function names
export * from "./openapi-client/sdk.gen";

// Backward compatibility aliases for commonly used functions
export {
  // Auth functions
  authAuthJwtLogin as authJwtLogin,
  authAuthJwtLogout as authJwtLogout,
  authRegisterRegister as registerRegister,
  authResetForgotPassword as resetForgotPassword,
  authResetResetPassword as resetResetPassword,
  authVerifyRequestToken as verifyRequestToken,
  authVerifyVerify as verifyVerify,

  // User functions
  usersUsersCurrentUser as usersCurrentUser,
  usersUsersPatchCurrentUser as usersPatchCurrentUser,
  usersUsersUser as usersUser,
  usersUsersPatchUser as usersPatchUser,
  usersUsersDeleteUser as usersDeleteUser,

  // Controls functions
  controlsCreateControl as createControl,
  controlsReadControls as readControls,
  controlsReadControl as readControl,
  controlsUpdateControl as updateControl,
  controlsDeleteControl as deleteControl,

  // Business Processes functions
  businessProcessesCreateBusinessProcess as createBusinessProcess,
  businessProcessesReadBusinessProcesses as readBusinessProcesses,
  businessProcessesReadBusinessProcess as readBusinessProcess,
  businessProcessesUpdateBusinessProcess as updateBusinessProcess,
  businessProcessesDeleteBusinessProcess as deleteBusinessProcess,

  // Risks functions
  risksCreateRisk as createRisk,
  risksReadRisks as readRisks,
  risksReadRisk as readRisk,
  risksUpdateRisk as updateRisk,
  risksDeleteRisk as deleteRisk,

  // Items functions
  itemReadItem as readItem,
  itemCreateItem as createItem,
  itemDeleteItem as deleteItem,

  // Suggestions functions
  suggestionsListSuggestions as listSuggestions,
  suggestionsUpdateSuggestionStatus as updateSuggestionStatus,

  // Documents functions
  documentsUploadDocument as uploadDocument,
  documentsListDocuments as listDocuments,
  documentsGetDocument as getDocument,
  documentsDeleteDocument as deleteDocument,
  documentsRenameDocument as renameDocument,
  documentsManuallyProcessDocument as manuallyProcessDocument,

  // Users functions (additional)
  usersCreateUser as createUser,
  usersListUsers as listUsers,
  usersGetCurrentUser as getCurrentUser,
  usersUpdateUserRole as updateUserRole,

  // Audit logs
  auditLogsListAuditLogs as listAuditLogs,

  // Dashboard
  dashboardGetDashboardMetrics as getDashboardMetrics,

  // Assessments (BPO)
  assessmentsGetPendingReviews as getPendingReviews,
  assessmentsGetSuggestionDetail as getSuggestionDetail,
  assessmentsSubmitAssessment as submitAssessment,

  // Mappings
  mappingsCreateMapping as createMapping,
  mappingsDeleteMapping as deleteMapping,
  mappingsGetMappingsForControl as getMappingsForControl,
  mappingsGetMappingsForRequirement as getMappingsForRequirement,

  // Regulatory frameworks
  regulatoryFrameworksCreateRegulatoryFramework as createRegulatoryFramework,
  regulatoryFrameworksReadRegulatoryFrameworks as readRegulatoryFrameworks,
  regulatoryFrameworksReadRegulatoryFramework as readRegulatoryFramework,
  regulatoryFrameworksUpdateRegulatoryFramework as updateRegulatoryFramework,
  regulatoryFrameworksDeleteRegulatoryFramework as deleteRegulatoryFramework,
  regulatoryFrameworksGetRegulatoryFrameworksTree as getRegulatoryFrameworksTree,
} from "./openapi-client/sdk.gen";

// Note: All types are already exported via export * from "./openapi-client"
// Note: All functions are already exported via export * from "./openapi-client/sdk.gen"