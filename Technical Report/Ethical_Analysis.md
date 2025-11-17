# Ethical Analysis

## Introduction to Ethical Considerations

The development of Momentum, a multi-discipline motorsport management simulation, necessitates careful consideration of ethical implications throughout its lifecycle. This analysis examines ethical issues across three distinct phases—before, during, and after project development—with reference to the ACM Code of Ethics and Professional Conduct. Three core principles guide this analysis: contributing to society and human well-being (ACM 1.1), avoiding harm (ACM 1.2), and respecting privacy (ACM 1.6).

## Stage 1: Before Starting the Project

### Stakeholder Impact Assessment (ACM 1.1: Contribute to Society)

Before commencing development, it was essential to evaluate how Momentum would contribute positively to society while identifying potential negative impacts. The ACM Code emphasizes that computing professionals should "contribute to society and to human well-being, acknowledging that all people are stakeholders in computing" (ACM, 2018). For this project, stakeholders include players, motorsport enthusiasts, aspiring team managers, and potentially educational institutions.

The primary ethical consideration was ensuring the simulation provides genuine educational value rather than merely trivializing motorsport management. To address this, the project scope deliberately incorporated realistic financial management, strategic decision-making, and technical component systems that mirror real-world complexities. This design decision ensures players develop understanding of resource allocation, risk management, and long-term planning—transferable skills applicable beyond gaming contexts.

However, a potential concern identified was the risk of promoting gambling-like behaviours through randomised outcomes in race simulations. To mitigate this, the Monte Carlo simulation system was designed to weight outcomes based on tangible factors (driver skill, team capability, vehicle performance) rather than pure chance. This ethical design choice ensures players understand that success derives from informed decisions rather than luck, promoting critical thinking over addictive gambling mechanics.

### Accessibility and Inclusivity Considerations (ACM 1.2: Avoid Harm)

Before implementation, consideration was given to avoiding harm through exclusionary design. The ACM principle 1.2 requires professionals to "avoid harm" by minimizing negative consequences, including those arising from discrimination or accessibility barriers. Initial design decisions addressed this by selecting PyQt6 as the GUI framework, which supports screen readers and keyboard navigation for users with disabilities.

The colour scheme selection process exemplified this ethical commitment. The Momentum theme utilises high-contrast colours (cyan #B9F2FF on charcoal #353839 background) specifically chosen to ensure readability for users with visual impairments, including those with colour vision deficiencies. This decision, made before writing any interface code, demonstrates proactive ethical consideration rather than retrofitting accessibility as an afterthought.

Furthermore, the decision to support borderless fullscreen as the default display mode was influenced by accessibility research suggesting that immersive, distraction-free interfaces benefit users with attention-related conditions. This choice reflects the ethical obligation to design for diverse user needs from the project's inception.

## Stage 2: During the Project

### Data Privacy and Security Implementation (ACM 1.6: Respect Privacy)

Throughout development, respecting user privacy remained paramount, particularly concerning save game data and potential future online features. ACM principle 1.6 mandates that computing professionals "respect privacy" by implementing appropriate safeguards and transparency measures. Although Momentum currently operates as a single-player application with local save files, architectural decisions made during development anticipate ethical data handling requirements.

The implementation of the save game system exemplifies this ethical approach. User career data is stored locally in JSON format within the `saves/` directory, ensuring users maintain complete control over their data. No telemetry, analytics, or usage tracking was implemented—a deliberate ethical choice prioritising user privacy over developer insight. The database schema design uses integer IDs and generated names rather than requiring any personal information, further minimising privacy risks.

Documentation within `API_KEY_SECURITY.md` established protocols for handling external API keys (specifically for currency exchange rates and potential name generation services). This documentation explicitly prohibits hardcoding sensitive credentials and mandates environment variable usage, demonstrating ethical consideration for security even when handling non-personal data. This approach educates future contributors about secure coding practices and establishes a privacy-conscious development culture.

### Intellectual Property and Attribution (ACM 1.5: Respect Property Rights)

During implementation, careful attention was paid to intellectual property ethics. The intelligent name generation system initially considered using third-party APIs (NameAPI, ParaNames) but ultimately selected the open-source Faker library specifically to avoid licensing complications and respect property rights. This decision, documented in `docs/NAME_GENERATION_SOLUTION.md`, demonstrates ethical consideration for both legal compliance and community norms around open-source software usage.

All third-party dependencies listed in `requirements.txt` utilise permissive licences (MIT, BSD, Apache 2.0), ensuring compliance with licensing terms. The project avoids incorporating real-world team names, driver identities, or official championship data without permission, instead generating fictional entities. This ethical stance prevents intellectual property infringement while maintaining simulation authenticity.

### Transparency and Code Quality (ACM 2.1: Strive for High Quality)

The ethical obligation to deliver high-quality, maintainable code manifested throughout development. Comprehensive documentation (README files, inline comments, API documentation) ensures transparency about system functionality and limitations. The logging system (`logging_system.py`) implements detailed error tracking and crash reporting, enabling users to understand system failures rather than experiencing opaque malfunctions. This transparency respects users' right to understand the technology they interact with.

Code structure deliberately prioritises readability and maintainability over clever optimisation, recognising that future contributors have an ethical right to understand and modify the codebase. The component system architecture, for instance, uses clear abstractions (ComponentFactory, ComponentManager, ComponentIntegration) with explicit interfaces documented in docstrings, reducing barriers to understanding and modification.

## Stage 3: After Completing the Project

### Ongoing Maintenance Responsibilities (ACM 1.2: Avoid Harm)

Post-development ethical obligations centre on avoiding harm through neglect. Abandoning software without maintenance pathways can harm users who depend on the application. Although Momentum remains a prototype academic project, the GitHub repository structure and comprehensive documentation prepare for potential community maintenance. The `HONEST_STATUS.md` file transparently communicates the project's incomplete state, managing user expectations and preventing harm from misrepresenting capabilities.

The decision to open-source the project (subject to academic submission requirements) reflects an ethical commitment to knowledge sharing and community benefit. By making the codebase publicly available, the project contributes to the broader computing community's learning resources, particularly for students studying game development, simulation design, or software architecture.

### Environmental and Resource Considerations (ACM 1.1: Contribute to Society)

Post-deployment ethical analysis must consider environmental impact. Momentum's architecture, particularly the Monte Carlo simulation system performing thousands of iterations per race, consumes computational resources. The ethical response involves optimising algorithms for efficiency—evident in the decision to cache simulation results and implement conditional component wear calculations only when necessary. These optimisations reduce energy consumption per session, demonstrating environmental responsibility.

Future development considerations documented in the project roadmap explicitly mention performance profiling and optimisation as ethical priorities, acknowledging that inefficient software contributes unnecessarily to energy consumption and, by extension, environmental degradation.

### User Support and Documentation Ethics (ACM 2.5: Give Comprehensive Evaluations)

The ethical obligation to provide honest, comprehensive evaluation extends beyond technical documentation to user expectations. The `PLAYABILITY_STATUS.md` document exemplifies this by clearly stating which features are functional, partially complete, or non-functional. This transparency prevents users from wasting time attempting to access non-existent features and demonstrates respect for their time and effort.

The crash reporting system generates detailed JSON reports with stack traces and system information, enabling users to provide meaningful bug reports. This ethical design recognises that users should be empowered to contribute to software improvement rather than being left frustrated by unexplained failures.

## Conclusion

Ethical considerations permeate every stage of Momentum's development lifecycle. Before starting, stakeholder impact assessment and accessibility planning established ethical foundations. During development, privacy protection, intellectual property respect, and transparency commitments guided implementation decisions. After completion, ongoing maintenance responsibilities, environmental awareness, and honest user communication continue the ethical commitment. By grounding these practices in ACM Code principles—particularly contributing to society (1.1), avoiding harm (1.2), and respecting privacy (1.6)—the project demonstrates that ethical computing extends far beyond mere legal compliance, embedding moral consideration into every architectural decision and implementation choice.

## References

Association for Computing Machinery (2018). *ACM Code of Ethics and Professional Conduct*. Available at: https://www.acm.org/code-of-ethics (Accessed: 12 November 2025).
