# ibe160 Architecture

## Project Context Understanding

I'm reviewing your project documentation for ibe160.
I see 5 epics with 15 total stories.
I also found your UX specification which defines the user experience requirements.

Key aspects I notice:
- The core functionality is an AI-powered gap analysis for GRC, acting as an "AI Legal Specialist" in a multi-tenant SaaS application.
- Critical NFRs include a robust and immutable audit trail, data security with encryption, multi-tenancy with RLS, and a Human-in-the-Loop (HITL) validation workflow.
- The UX is desktop-first, centered on an "Action-Oriented Hub" dashboard, and features a novel two-stage "AI Review Mode" for triaging and approving AI suggestions.
- The unique challenge is building trust in the AI's "legal specialist" persona and ensuring its suggestions are seamlessly integrated into an accountable, human-validated workflow.

This will help me guide you through the architectural decisions needed to ensure AI agents implement this consistently.

## Starter Template Decision

Based on the project's technical specifications, the `vintasoftware/nextjs-fastapi-template` has been chosen as the foundational starter template.

**Project Initialization Note:** The first implementation story will be to initialize the project repository. This is a multi-step process:
1. Create a new repository from the `vintasoftware/nextjs-fastapi-template`.
2. Clone the new repository.
3. Install dependencies (`uv`, `pnpm`).
4. Configure environment variables (`.env`).
5. Run the application using the provided `docker compose` commands.

### Decisions Provided by Starter

The following architectural decisions are provided by the starter and will be marked as such in our decision log:

- **Language/TypeScript:** End-to-end type safety with TypeScript for the frontend and Python with Pydantic for the backend.
- **Styling Solution:** Tailwind CSS via the integrated Shadcn/UI component library.
- **Testing Framework:** Pytest for the backend. Pre-commit hooks are included for static checks.
- **Linting/Formatting:** Provided by pre-commit hooks.
- **Build Tooling:** A combination of `uv` (for Python), `pnpm` (for Node.js), `Docker Compose`, and `make`.
- **Project Structure:** A monorepo with distinct `frontend` and `backend` directories.
- **Authentication:** A production-ready system using `fastapi-users`.

## Decision Identification

I have analyzed the project requirements and identified approximately **15** key architectural decisions required for a robust foundation. The chosen starter template automatically handles **8** of these.

We will focus on the **7 remaining critical decisions** together:

**Critical Decisions (Must be made now):**
1.  **Data Persistence:** Confirming the primary database choice.
2.  **Deployment Targets:** Confirming the hosting for the frontend and backend.
3.  **AI & Vector Database:** Choosing the services for AI processing and storing embeddings.

**Important Decisions (Shape the architecture):**
4.  **Real-time Updates:** How the application will push live updates to the user interface.
5.  **File Storage:** Where and how to store uploaded regulatory documents.
6.  **Background Jobs:** How to handle long-running tasks like AI analysis without freezing the app.

**Future-Facing Decisions (Can be deferred but good to consider):**
7.  **Email Service:** How the application will send notifications (post-MVP).
