# Technical Research Report: Backend Deployment Strategy

**Date:** November 17, 2025
**Author:** Mary, Business Analyst
**Status:** Completed

## 1. Executive Summary

This report analyzes the optimal deployment strategy for the FastAPI backend of the "Risk Control Matrix" project. The initial proposal to use Vercel for the backend was found to be a critical risk due to serverless function timeouts that would interfere with the core AI features. After evaluating three viable alternatives—Render, Railway, and Fly.io—the final recommendation is to adopt a hybrid deployment model:

*   **Frontend (Next.js):** Host on **Vercel** to leverage its best-in-class frontend hosting.
*   **Backend (FastAPI):** Host on **Railway** to provide a robust, persistent, and cost-effective environment that supports long-running tasks and offers a superior developer experience for testing.

## 2. The Technical Question

The primary technical question was to evaluate the suitability of Vercel for hosting the project's FastAPI backend, as suggested in the `proposal.md`, and to explore and recommend alternatives if Vercel was found to be a poor fit. The core of the problem revolved around supporting long-running API calls for the AI-assisted workflow.

## 3. Project Context & Constraints

*   **Project:** A "Risk Control Matrix" web application.
*   **Technology Stack:** Next.js (Frontend), FastAPI (Backend), Supabase (Database), OpenAI GPT-4 (AI).
*   **Key Requirement:** The backend must reliably handle long-running API calls for AI-powered analysis of regulatory documents.
*   **Developer Constraint:** The user's skill level is "beginner," prioritizing ease of use and a smooth developer experience.
*   **Budget Constraint:** The solution must be free or very low-cost during the development and testing phase.

## 4. Technology Options Evaluated

Four platforms were considered for hosting the FastAPI backend:

1.  **Vercel:** The initially proposed platform.
2.  **Render:** A popular Platform-as-a-Service (PaaS).
3.  **Railway:** A modern PaaS focused on developer experience and usage-based pricing.
4.  **Fly.io:** A platform for deploying applications in globally distributed micro-VMs.

## 5. Comparative Analysis

| Feature | Vercel (for Backend) | Render | Railway | Fly.io |
| :--- | :--- | :--- | :--- | :--- |
| **Long-Running Tasks**| **No (Critical Flaw)** | Yes | Yes | Yes |
| **Free Tier Sleeps?** | N/A (Stateless) | **Yes** | **No** | **No** |
| **Ease of Use** | High | Very High | **Very High** | Medium |
| **Pricing Model** | Usage-Based | Predictable, Per-Service | Usage-Based | Usage-Based |
| **Best For...** | Simple, stateless APIs | Predictable costs, clear roles | **Simplicity, MVP cost, DX** | Global low-latency, control |

## 6. Decision & Recommendation

The decision was driven by three key priorities identified during our research:
1.  **Must support long-running tasks** to avoid breaking the core AI features.
2.  **Must have an "always-on" free tier** for a smooth development and testing workflow.
3.  **Must be easy to use** for a beginner.

Based on these priorities, **Railway is the clear winner.**

*   It solves the critical timeout issue found with Vercel.
*   Its "always-on" free tier is superior to Render's for active development.
*   It is significantly easier to get started with than Fly.io.

**Final Recommendation:** Proceed with deploying the FastAPI backend to **Railway**.

## 7. Proposed Architecture

A hybrid deployment model is recommended:

1.  **Frontend (Vercel):** The Next.js application is deployed to Vercel. An environment variable (`NEXT_PUBLIC_API_URL`) will point to the backend's public URL.
2.  **Backend (Railway):** The FastAPI application is deployed to Railway, which provides a stable public URL.
3.  **CORS:** The FastAPI backend will be configured with CORS middleware to accept requests from the Vercel frontend domain.

This architecture leverages the best platform for each part of the stack, ensuring performance, reliability, and an excellent developer experience.
