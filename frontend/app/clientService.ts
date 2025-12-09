// Export everything from the generated client
export * from "./openapi-client";

// Import the client configuration (interceptors, etc.)
import "@/lib/clientConfig";

// Import specific functions and types to alias them
import {
  authAuthJwtLogin,
  authAuthJwtLogout,
  authRegisterRegister,
  authResetForgotPassword,
  authResetResetPassword,
  authVerifyRequestToken,
  authVerifyVerify,
  itemReadItem,
  itemCreateItem,
  itemDeleteItem,
  controlsCreateControl,
  controlsReadControls,
  controlsReadControl,
  controlsUpdateControl,
  controlsDeleteControl,
  risksCreateRisk,
  risksReadRisks,
  risksReadRisk,
  risksUpdateRisk,
  risksDeleteRisk,
  businessProcessesCreateBusinessProcess,
  businessProcessesReadBusinessProcesses,
  businessProcessesReadBusinessProcess,
  businessProcessesUpdateBusinessProcess,
  businessProcessesDeleteBusinessProcess,
  regulatoryFrameworksCreateRegulatoryFramework,
  regulatoryFrameworksReadRegulatoryFrameworks,
  regulatoryFrameworksReadRegulatoryFramework,
  regulatoryFrameworksUpdateRegulatoryFramework,
  regulatoryFrameworksDeleteRegulatoryFramework,
} from "./openapi-client";

import {
  AuthAuthJwtLoginError,
  AuthRegisterRegisterError,
  // Add other error types if needed
} from "./openapi-client";

// --- Aliases for Backward Compatibility / Cleaner Code ---

// Auth
export const authJwtLogin = authAuthJwtLogin;
export const authJwtLogout = authAuthJwtLogout;
export const registerRegister = authRegisterRegister;
export const resetForgotPassword = authResetForgotPassword;
export const resetResetPassword = authResetResetPassword;
export const verifyRequestToken = authVerifyRequestToken;
export const verifyVerify = authVerifyVerify;

export type AuthJwtLoginError = AuthAuthJwtLoginError;
export type RegisterRegisterError = AuthRegisterRegisterError;

// Items
export const readItem = itemReadItem;
export const createItem = itemCreateItem;
export const deleteItem = itemDeleteItem;

// Controls
export const createControl = controlsCreateControl;
export const readControls = controlsReadControls;
export const readControl = controlsReadControl;
export const updateControl = controlsUpdateControl;
export const deleteControl = controlsDeleteControl;

// Risks
export const createRisk = risksCreateRisk;
export const readRisks = risksReadRisks;
export const readRisk = risksReadRisk;
export const updateRisk = risksUpdateRisk;
export const deleteRisk = risksDeleteRisk;

// Business Processes
export const createBusinessProcess = businessProcessesCreateBusinessProcess;
export const readBusinessProcesses = businessProcessesReadBusinessProcesses;
export const readBusinessProcess = businessProcessesReadBusinessProcess;
export const updateBusinessProcess = businessProcessesUpdateBusinessProcess;
export const deleteBusinessProcess = businessProcessesDeleteBusinessProcess;

// Regulatory Frameworks
export const createRegulatoryFramework = regulatoryFrameworksCreateRegulatoryFramework;
export const readRegulatoryFrameworks = regulatoryFrameworksReadRegulatoryFrameworks;
export const readRegulatoryFramework = regulatoryFrameworksReadRegulatoryFramework;
export const updateRegulatoryFramework = regulatoryFrameworksUpdateRegulatoryFramework;
export const deleteRegulatoryFramework = regulatoryFrameworksDeleteRegulatoryFramework;