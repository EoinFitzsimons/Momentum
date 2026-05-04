# Testing

## Testing Strategy

Momentum is tested with two equally important goals: prove that the system works correctly, and prove that it continues to work as complexity increases. The strategy is layered on purpose. Small logic checks are used first, then full workflow checks, and then complete race and season simulations are run to observe behaviour under realistic load and state transitions.

This approach reflects the effort needed in a simulation project where many subsystems interact. A race outcome is not created by one function; it is produced by configuration, simulation logic, data storage, standings updates, and interface response all working together. For that reason, testing is repeated at each stage of integration, not only at the end.

## Functional Requirements Testing

Functional testing checks whether the game behaves as intended from both a user and system perspective. This includes race setup, race execution, result creation, standings progression, and management actions such as team and staff changes. The objective is to verify visible outcomes and state integrity, not just isolated code outputs.

A key part of the effort was tracing failures back to the correct layer. Some defects appear as interface problems but are rooted in data state. Others appear as simulation problems but are caused by integration assumptions. Functional testing was therefore designed to observe complete action chains, so each requirement could be validated as an end-to-end behaviour.

The functional evidence is grouped as follows:

- Unit checks confirm individual calculations and rule logic.
- Integration checks confirm that services, storage, and interfaces work together.
- Data-shape checks confirm that stored and exchanged data remains valid and consistent.

## Non-Functional Requirements Testing

Non-functional testing measures quality rather than feature presence. This includes speed, repeatability, interface readability, keyboard accessibility, and consistency under longer sessions. These areas require different validation methods than functional checks, because a feature may be technically correct while still feeling unreliable or difficult to use.

This area required sustained effort because the criteria are broader and often harder to measure directly. Performance and repeatability can be quantified through repeated runs, while interface quality and accessibility require structured interaction checks. The testing process therefore combines measurable checks with controlled user-facing review.

The non-functional evidence includes:

- Repeatability checks to confirm the same inputs produce the same results where determinism is expected.
- Performance checks to measure simulation speed and response under load.
- Interface checks to confirm controls are visible, usable, and consistent.
- Requirement-status reviews to track what is fully complete, partially complete, or deferred.

## Automation and CI/CD

Automated checking runs continuously as the project changes so regressions are detected early. The pipeline verifies requirements artifacts, validates structured data, runs repeatability and integration checks, and performs code-quality checks. This reduces manual overhead and makes quality evidence repeatable over time.

The value of this automation is practical: it protects progress already made. In a project with frequent iteration, the risk is not only new bugs, but old bugs returning. Automated checks reduce that risk and support faster, safer development cycles.

## Unit Testing

Unit testing validates small pieces of logic independently, such as progression rules, race calculations, and utility behaviour. This is the fastest way to detect incorrect assumptions and edge-case failures before they spread into larger workflows.

Strong unit coverage also improves change confidence. When a calculation is adjusted or tuned, local checks immediately show whether the change preserved expected behaviour.

## Integration Testing

Integration testing checks how components behave together. It confirms that simulation services, persistence, and user-facing flows remain in sync when data moves across modules. These checks are essential for validating complete workflows such as race execution, result storage, and standings progression.

Integration work reflects a significant part of project effort because interaction faults are often subtle. A workflow may pass local checks yet fail when timing, state transitions, or data ordering changes under realistic usage.

## System Testing

System testing runs the full application in realistic conditions. Longer simulations are used to observe behaviour over time, identify bottlenecks, and check that cumulative state remains stable. This stage verifies that the project behaves like a complete product, not only a collection of validated parts.

This is where effort in earlier stages is stress-tested. Stability over time is especially important in management simulation, where small state errors can compound across multiple events.

## User Evaluation

User evaluation focuses on clarity, control, and confidence. Participants complete realistic tasks such as configuring races, reviewing outcomes, and managing team decisions. Feedback is gathered on ease of use, realism, and responsiveness.

This stage helps bridge a common gap in technical projects: something can be correct but still feel difficult or unclear. User evaluation identifies those gaps and turns them into concrete improvement targets.

Overall, the testing approach demonstrates substantial development effort across correctness, stability, and usability. It gives a clear picture of what is already dependable, what remains in progress, and where future work should be prioritised.