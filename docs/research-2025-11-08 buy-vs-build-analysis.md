# Buy vs. Build Analysis: Risk Control Matrix

**Date:** Saturday, November 8, 2025

## 1. Introduction

This document analyzes the trade-offs between building a custom Risk Control Matrix solution and buying an existing Governance, Risk, and Compliance (GRC) tool. The goal is to determine which approach best aligns with our project's objectives, timeline, and budget as outlined in `proposal.md`.

---

## 2. Evaluation Criteria

The following criteria, derived from the "Must Have (MVP)" and "Technical Constraints" sections of `proposal.md`, will be used to evaluate potential off-the-shelf solutions.

### Functional Criteria (Must-Haves)
*   **Role-Based Authentication:** Must support distinct roles (Admin, Business Process Owner, Executive, General User) with corresponding permissions.
*   **Flexible Data Table:** Must provide a customizable table for the core risk matrix with CRUD functionality.
*   **Risk Register:** Must have a dedicated module for documenting and managing business risks.
*   **Control Library:** Must offer a centralized library for defining and managing internal controls.
*   **Dashboard & Reporting:** Must provide a visual dashboard for a high-level overview of the organization's risk posture.
*   **Regulatory Framework Mapping:** Must allow users to map internal controls to external laws and regulations to perform gap analysis.
*   **Filtering and Sorting:** Must have powerful filtering and sorting capabilities on the main data table.
*   **AI-Assisted Workflow:** Must leverage AI to analyze regulatory documents, suggest risks, and recommend controls.

### Technical Criteria
*   **Web-Based Application:** Must be a responsive, browser-based application.
*   **Audit Trail:** Must log all critical changes to data (who, what, when).
*   **Data Security:** Must support encryption of data at rest and in transit.
*   **Integration/API Access:** Must provide an API for potential future integrations.

### Business Criteria
*   **Cost:** Total Cost of Ownership (TCO), including subscription fees, implementation costs, and maintenance.
*   **Time to Market:** How quickly can the solution be implemented and adopted by users?
*   **Customizability:** How easily can the solution be adapted to our specific user flows and data requirements?
*   **Scalability:** Can the solution support our expected user load and data growth?

---

## 3. Market Research

This section provides a brief overview of the top GRC tools identified as potential alternatives.

*   **Alternative 1: MetricStream**
    *   **Overview:** A comprehensive GRC platform with extensive AI capabilities for compliance intelligence, regulatory tracking, risk forecasting, and AI-powered recommendations. It is a well-established player in the GRC market.
*   **Alternative 2: Drata**
    *   **Overview:** An "AI-native" platform focused on automating compliance, managing risk, and accelerating security reviews. It emphasizes continuous control monitoring and automated evidence collection.
*   **Alternative 3: IBM OpenPages**
    *   **Overview:** An AI-driven, enterprise-grade GRC platform from a major technology vendor. It focuses on consolidating risk management functions, real-time risk monitoring, and compliance automation.

---

## 4. Comparative Analysis

This section contains a high-level comparison of the identified alternatives against our custom-build proposal. "Likely" indicates features that are standard for this type of software but were not explicitly confirmed in the initial search. "Varies" indicates features that are typically configurable or available in higher-tier plans.

| Criteria | Custom Build (Proposed) | MetricStream | Drata | IBM OpenPages |
| :--- | :--- | :--- | :--- | :--- |
| **Functional Criteria** | | | | |
| Role-Based Auth | Yes | Likely | Likely | Yes |
| Data Table | Yes | Likely | Likely | Likely |
| Risk Register | Yes | Yes | Yes | Yes |
| Control Library | Yes | Yes | Yes | Yes |
| Dashboard | Yes | Yes | Yes | Yes |
| Regulatory Mapping | Yes | Yes | Yes | Yes |
| Filtering/Sorting | Yes | Likely | Likely | Likely |
| AI-Assisted Workflow | Yes | Yes | Yes | Yes |
| **Technical Criteria** | | | | |
| Web-Based | Yes | Yes | Yes | Yes |
| Audit Trail | Yes | Likely | Likely | Likely |
| Data Security | Yes | Likely | Likely | Likely |
| API Access | Yes | Varies | Varies | Varies |
| **Business Criteria** | | | | |
| Cost | Development cost + hosting | High (Enterprise Subscription) | Medium-High (SaaS Subscription) | High (Enterprise Subscription) |
| Time to Market | 4 weeks (MVP) | Weeks to Months (Implementation) | Weeks (Implementation) | Months (Implementation) |
| Customizability | High | Medium | Low-Medium | Medium |
| Scalability | High (custom architecture) | High | High | High |

---

## 5. Summary and Recommendation

This section summarizes the findings and provides a preliminary recommendation on whether to buy or build.

### Build Option
*   **Pros:**
    *   **High Customizability:** The solution can be tailored to the exact workflows, data models, and user experiences defined in `proposal.md`.
    *   **Full Control:** We have complete control over the technology stack, future roadmap, and feature prioritization.
    *   **Potentially Lower TCO:** While requiring an initial investment, building avoids recurring high subscription fees, which may lead to a lower Total Cost of Ownership over the long term.
    *   **Specific AI Implementation:** We can build the AI-assisted workflows to our exact specifications, ensuring they are deeply integrated and optimized for our use case.
*   **Cons:**
    *   **Development & Maintenance Burden:** We are fully responsible for all development, ongoing maintenance, bug fixes, and support.
    *   **Ambitious Timeline:** The 4-week timeline for the MVP is aggressive and carries the risk of delays.
    *   **Initial Cost:** Requires an upfront investment in development resources.

### Buy Option
*   **Pros:**
    *   **Faster Time to Market:** The core software is already built, allowing for a potentially faster deployment (though implementation can still take weeks or months).
    *   **Reduced Maintenance Overhead:** The vendor handles maintenance, updates, and bug fixes.
    *   **Built-in Expertise:** These platforms are built by experts in GRC and often include best practices and a rich feature set beyond our MVP.
    *   **Vendor Support:** Comes with a dedicated support channel for resolving issues.
*   **Cons:**
    *   **High Cost:** Enterprise GRC software typically involves significant and recurring subscription fees.
    *   **Lower Customizability:** We would have to adapt our processes to the software's workflows, which may not perfectly match the specific user flows in `proposal.md`.
    *   **Vendor Lock-in:** We become dependent on the vendor for future updates, features, and pricing changes.
    *   **Generic AI Features:** The AI capabilities may be more generic and less tailored to our specific needs for analyzing regulatory documents and suggesting controls.

### Preliminary Recommendation: **Build**

Based on this initial analysis, the **Build** option appears to be the more favorable approach for this project.

The `proposal.md` outlines a very specific, highly customized solution with unique user flows and a deeply integrated, custom-tailored AI workflow. It is unlikely that an off-the-shelf product could meet these precise requirements without significant, costly, and complex customization that would negate many of the benefits of buying.

While the "Buy" option offers a faster path to a generic solution, the "Build" option provides the control and flexibility necessary to realize the specific vision of the project and deliver the maximum value to our target users.

This recommendation is based on the assumption that the primary goal is to create a solution that perfectly matches the detailed specification, rather than deploying a generic GRC tool as quickly as possible.
