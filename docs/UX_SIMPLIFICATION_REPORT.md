# UX simplification report

The first-use experience now leads with one promise and two actions: start a decision or open an existing project. It explains the distinction between a Project (the portfolio container) and a Decision Case (one decision to analyze), then shows the complete nine-stage journey: Project → Decision → Context → Options → Evidence → Analysis → Recommendation → Approval → Action.

Navigation labels were simplified to decision-language, the new-case prompt asks the user directly what decision they are making, and technical concepts remain behind contextual help. Arabic and English use the same information hierarchy, with RTL/LTR document direction and responsive mobile navigation.

Verification on 2026-08-14: Playwright passed 4/4 combinations (Arabic/English × Desktop Chrome/Pixel 7), including headline, CTA destinations, decision journey, Project/Decision Case explanation, and viewport containment. The React review preserved shared components (`DecisionJourney`, `DecisionWorkflow`) instead of duplicating the journey in individual pages.
