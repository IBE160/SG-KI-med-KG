# Supabase Configuration Guide for Story 2.1

This guide details the manual configuration steps required in the Supabase Dashboard to support the "Implement User Registration & Login" story.

## 1. Authentication Providers

1.  Navigate to **Authentication > Providers** in your Supabase Dashboard.
2.  Enable **Email**.
3.  Ensure **Confirm email** is enabled (to satisfy AC #3).
4.  Ensure **Secure password** is enabled (AC #2).

## 2. Email Templates

1.  Navigate to **Authentication > Email Templates**.
2.  **Confirm Your Signup**:
    -   Ensure the template includes the `{{ .ConfirmationURL }}` variable.
    -   Customize the subject if desired (e.g., "Confirm your ibe160 account").
3.  **Reset Password**:
    -   Ensure the template includes the `{{ .ConfirmationURL }}` variable.
    -   Subject: "Reset your ibe160 password".

## 3. Password Protection

1.  Navigate to **Authentication > Rate Limits**.
    -   Configure appropriate rate limits for sign-ups and sign-ins to prevent abuse.
2.  Navigate to **Authentication > Password Protection**.
    -   Set **Minimum password length** to **8** (AC #2).
    -   Enable **Require strong passwords** (mixed case, numbers, symbols) if available in your tier, or rely on frontend/backend validation (we implemented Zod/Pydantic validation to enforce this).

## 4. SMTP / SendGrid Configuration (Optional but Recommended)

For production reliability (AC #3), configure a custom SMTP server:

1.  Navigate to **Project Settings > Authentication > SMTP Settings**.
2.  Enable **Enable Custom SMTP**.
3.  Fill in your SendGrid details:
    -   **Sender Email**: `no-reply@yourdomain.com` (or your verified SendGrid sender).
    -   **Sender Name**: `ibe160 Risk Platform`.
    -   **Host**: `smtp.sendgrid.net`.
    -   **Port**: `587`.
    -   **Username**: `apikey`.
    -   **Password**: Your SendGrid API Key.

## 5. Database & RLS

1.  Navigate to **Authentication > Policies**.
2.  Ensure RLS is enabled on the `users` table (managed by Supabase Auth) and any custom tables we create.
3.  (Note: We will handle custom RLS policies in our migration scripts).

## 6. Environment Variables

Ensure these keys are present in your local environment files:

**Frontend (`frontend/.env.local`):**
```bash
NEXT_PUBLIC_SUPABASE_URL=your-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

**Backend (`backend/.env`):**
```bash
SUPABASE_URL=your-project-url
SUPABASE_JWT_SECRET=your-project-jwt-secret
# Note: SUPABASE_JWT_SECRET is found in Project Settings > API > JWT Settings
```
