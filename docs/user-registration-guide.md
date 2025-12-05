# User Registration & Account Management: A Comprehensive Guide

**Date:** 2025-12-05
**Author:** Amelia (Developer Agent)
**Project:** ibe160

## Overview

This document outlines the various methods for user registration and account management within the ibe160 application, leveraging Supabase Auth as the primary identity provider. Understanding these methods is crucial for both end-users and administrators.

## 1. User Self-Registration (Frontend Application)

This is the standard and most common method for users to create an account.

**Flow:**
1.  **Access Registration Page:** A new user navigates to the `/register` page in the frontend application.
2.  **Provide Credentials:** The user enters their desired email address and password.
3.  **Supabase `signUp`:** The frontend (via `frontend/app/(auth)/register/page.tsx`) calls `supabase.auth.signUp()` with the provided credentials.
4.  **Email Verification:** Supabase creates an entry in its `auth.users` table and automatically sends a verification email to the user (configured via Supabase Dashboard).
5.  **Email Confirmation:** The user clicks the link in the verification email, confirming their account.
6.  **Automatic Database Sync:** **(NEWLY IMPLEMENTED)** A database trigger (`public.handle_new_user()`) in Supabase automatically creates a corresponding entry in our `public.user` table (`id`, `email`, `role='general_user'`, `tenant_id='00000000-0000-0000-0000-000000000000'`) whenever a new user is created in `auth.users`. This ensures data consistency with our application's `User` model.
7.  **Login:** The user can now log in via the `/login` page.

**Use Case:** Ideal for new users discovering the application, allowing them to create an account independently.

## 2. Administrator-Initiated Registration (Supabase Dashboard)

Administrators can manually create user accounts directly through the Supabase Dashboard. This is useful for onboarding specific users or testing purposes.

**Flow:**
1.  **Access Supabase Dashboard:** An administrator logs into the Supabase project dashboard.
2.  **Navigate to Authentication:** Go to the "Authentication" section in the sidebar.
3.  **Add User:** Click the "Users" tab and then "Add User".
4.  **Enter Details:** Provide the email and password for the new user.
5.  **Email Verification (Optional):** You can choose whether to send a verification email or instantly verify the user.
6.  **Automatic Database Sync:** Similar to self-registration, the `public.handle_new_user()` trigger will automatically create a corresponding entry in our `public.user` table.

**Use Case:** Manual onboarding of specific users, internal testing, or when a user needs to be created without going through the frontend flow.

## 3. Bootstrapping the First Administrator Account

To manage user roles (especially making other users Admins) using the application's UI, you first need at least one user with the `admin` role in your database. This involves a one-time manual step.

**Flow:**
1.  **Self-Register:** Register yourself as a normal user through the frontend application (Method 1).
2.  **Access Supabase SQL Editor:** Log into your Supabase project dashboard and navigate to the "SQL Editor".
3.  **Execute SQL for Role Update:**
    *   First, find your user ID from the `auth.users` table:
        ```sql
        SELECT id, email FROM auth.users WHERE email = 'your_registered_email@example.com';
        ```
    *   Then, update the `role` and `tenant_id` in your `public.user` table. (The `handle_new_user` trigger will have created a `public.user` entry for you already). Replace `YOUR_UUID_HERE` with the ID from the previous step.
        ```sql
        UPDATE public.user
        SET role = 'admin',
            tenant_id = '00000000-0000-0000-0000-000000000000' -- Use the fixed placeholder or a specific tenant ID if available
        WHERE id = 'YOUR_UUID_HERE';
        ```
    *   **Note on `tenant_id`:** The trigger currently defaults `tenant_id` to `00000000-0000-0000-0000-000000000000`. You might need to update this to a real tenant ID later if multi-tenancy involves different tenant UUIDs.

**Use Case:** Setting up the initial administrator account after a fresh deployment.

## 4. Account Management (Admin UI)

Once you have at least one Admin user (bootstrapped via Method 3), you can manage other user accounts and their roles through the application's dedicated Admin UI.

**Flow:**
1.  **Login as Admin:** Log into the ibe160 application as a user with the `admin` role.
2.  **Navigate to User Management:** Access the `/dashboard/admin/users` page.
3.  **Edit User Roles:** From this interface, you can select any user and change their assigned role (Admin, BPO, Executive, General User).
4.  **Role Persistence:** The role change is persisted in our `public.user` table via the backend API.

**Use Case:** Day-to-day management of user roles and permissions by an application administrator.

This comprehensive approach ensures flexible and secure user management throughout the application's lifecycle.
