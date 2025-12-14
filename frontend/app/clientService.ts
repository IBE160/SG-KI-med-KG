// Export everything from the generated client
export * from "./openapi-client";

// Import the client configuration (interceptors, etc.)
import "@/lib/clientConfig";

// Re-export the SDK with all generated function names
export * from "./openapi-client/sdk.gen";

// Backward compatibility aliases for commonly used auth functions
export {
  authAuthJwtLogin as authJwtLogin,
  authAuthJwtLogout as authJwtLogout,
  authRegisterRegister as registerRegister,
  authResetForgotPassword as resetForgotPassword,
  authResetResetPassword as resetResetPassword,
  authVerifyRequestToken as verifyRequestToken,
  authVerifyVerify as verifyVerify,
  usersUsersCurrentUser as usersCurrentUser,
  usersUsersPatchCurrentUser as usersPatchCurrentUser,
  usersUsersUser as usersUser,
  usersUsersPatchUser as usersPatchUser,
  usersUsersDeleteUser as usersDeleteUser,
} from "./openapi-client/sdk.gen";

// Note: All types are already exported via export * from "./openapi-client"
// Note: All functions are already exported via export * from "./openapi-client/sdk.gen"