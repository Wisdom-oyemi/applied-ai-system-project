# PawPal+ System Diagram (Mermaid)

This diagram emphasizes the current PawPal+ reliability-oriented architecture.

```mermaid
flowchart TD
    A[User Input\nOwner, pets, tasks, constraints] --> B[Planner/Scheduler Engine\nFilter due+pending\nSort by priority/time\nFit to time budget\nDetect conflicts]
    B --> C[Plan Output\nSchedule + reasoning + warnings]
    C --> D[Human Review\nOwner checks practicality/safety]
    D --> E[Feedback Loop\nEdit tasks/constraints and regenerate]
    E --> B

    subgraph Q[Quality and Reliability Layer]
        T[Automated Tester\nUnit and integration tests]
        V[Evaluator\nConsistency and rule checks]
        R[Regression Gate\nRun tests on rule changes]
    end

    B -. validates logic .-> T
    C -. scored by .-> V
    R -. blocks bad changes .-> B
    T --> R
    V --> R

    H[Developer] --> T
    H --> V
```

## Notes

- Core architecture is deterministic scheduling rather than LLM generation.
- Human and automated checks both exist to increase trust in schedule quality.
