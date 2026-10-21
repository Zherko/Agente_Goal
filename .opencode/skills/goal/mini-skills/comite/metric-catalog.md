# Metric Catalog

Predefined metric templates by comparison domain. The metric-selector agent reads this file to quickly select relevant metrics for a given domain.

## How to Use

1. Detect the comparison domain (Step 0 of comparison flow)
2. Look up the domain below
3. Select 5-10 metrics from the template
4. Adjust weights (1-3) based on the specific comparison context
5. If the domain is not listed, generate metrics from first principles

---

## Framework / Tool

For comparing frontend frameworks, backend frameworks, libraries, developer tools.

| Metric | Default Weight | Source Type | What to Check |
|--------|---------------|-------------|---------------|
| Rendimiento | 3 | Benchmarks | Lighthouse scores, render speed, memory usage |
| Learning curve | 2 | Docs + community | Time to first CRUD app, documentation quality |
| Ecosistema | 3 | npm/PyPI/crates.io | Downloads, packages available, plugins |
| Comunidad | 2 | GitHub + Stack Overflow | Stars, contributors, SO questions, Discord activity |
| Documentación | 2 | Official sites | Completeness, examples, tutorials, API docs |
| TypeScript/Types | 1 | Official repos | Native support, type quality, DefinitelyTyped |
| Mantenimiento | 2 | GitHub + changelog | Release frequency, LTS policy, bus factor |
| Bundle size | 1 | Bundlephobia | Min+gz size, tree-shaking support |
| Testing | 2 | Official + community | Test framework, mocking, E2E support |
| Deployment | 1 | Docs | Docker, serverless, static hosting support |

**Typical selection:** 7 metrics (Rendimiento, Learning curve, Ecosistema, Comunidad, Documentación, TypeScript, Mantenimiento)

---

## Platform / Service

For comparing cloud providers, SaaS tools, hosting, APIs.

| Metric | Default Weight | Source Type | What to Check |
|--------|---------------|-------------|---------------|
| Precio | 3 | Pricing pages | Tiers, free tier, cost at scale (1K/10K/100K users) |
| Features | 3 | Official docs | Core features, unique features, feature gaps |
| Escalabilidad | 2 | Architecture docs | Auto-scaling, limits, performance at scale |
| Integraciones | 2 | Marketplace | API, webhooks, third-party integrations |
| Soporte | 2 | Support pages | Channels, response time, documentation |
| Seguridad | 2 | Compliance pages | SOC2, GDPR, encryption, SSO |
| Uptime | 2 | Status pages | SLA, historical uptime, incident history |
| UX | 2 | Hands-on | Dashboard, onboarding, workflow simplicity |
| Comunidad | 1 | GitHub + forums | Open-source components, community size |
| Lock-in | 1 | Architecture | Vendor lock-in risk, portability, export options |

**Typical selection:** 6-7 metrics (Precio, Features, Escalabilidad, Soporte, Seguridad, Uptime)

---

## Programming Language

For comparing programming languages.

| Metric | Default Weight | Source Type | What to Check |
|--------|---------------|-------------|---------------|
| Velocidad | 3 | Benchmarks | Execution speed, startup time, memory usage |
| Sintaxis | 2 | Official docs | Readability, verbosity, sugar features |
| Ecosistema | 3 | Package registries | Libraries, frameworks, tools available |
| Empleabilidad | 2 | Job boards | Job demand, salary ranges, market trend |
| Documentación | 2 | Official sites | Language spec, tutorials, books |
| Testing | 1 | Ecosystem | Built-in test framework, assertion libraries |
| Tooling | 2 | Ecosystem | IDE support, linters, formatters, debuggers |
| Concurrency | 1 | Docs + benchmarks | Threading model, async/await, parallelism |
| Interop | 1 | Docs | FFI, calling C/OS, interop with other languages |
| Community | 1 | GitHub + conferences | Activity, conferences, meetups |

**Typical selection:** 7 metrics (Velocidad, Sintaxis, Ecosistema, Empleabilidad, Documentación, Testing, Tooling)

---

## Strategy / Business

For comparing business strategies, go-to-market approaches, pricing models.

| Metric | Default Weight | Source Type | What to Check |
|--------|---------------|-------------|---------------|
| ROI | 3 | Case studies | Expected return, payback period, TCO |
| Riesgo | 2 | Analysis | Downside scenarios, probability of failure |
| Tiempo al mercado | 2 | Estimates | Speed to launch, time to first revenue |
| Escalabilidad | 2 | Market analysis | Growth potential, market size, expansion path |
| Competencia | 2 | Market research | Existing players, differentiation, moat |
| Barreras de entrada | 1 | Industry analysis | Capital required, regulatory, technical barriers |
| Unit economics | 2 | Financial models | CAC, LTV, margins, break-even point |
| Flexibilidad | 1 | Strategic analysis | Ability to pivot, optionality, reversibility |
| Talento | 1 | Labor market | Team availability, skill requirements |
| Timing | 1 | Market trends | Market readiness, trend alignment |

**Typical selection:** 6 metrics (ROI, Riesgo, Tiempo al mercado, Escalabilidad, Competencia, Unit economics)

---

## ML / Data Science

For comparing ML models, algorithms, data approaches.

| Metric | Default Weight | Source Type | What to Check |
|--------|---------------|-------------|---------------|
| Accuracy | 3 | Papers + benchmarks | F1, AUC, precision, recall on standard datasets |
| Velocidad entrenamiento | 2 | Benchmarks | Time to train, GPU/CPU requirements |
| Velocidad inferencia | 2 | Benchmarks | Latency, throughput, real-time capability |
| Interpretabilidad | 2 | Papers + docs | SHAP, feature importance, explainability |
| Datos requeridos | 2 | Papers | Minimum data needed, cold start behavior |
| Complejidad | 1 | Implementation | Code complexity, debugging difficulty |
| Robustez | 2 | Papers + tests | Noise handling, outlier resistance, adversarial |
| Escalabilidad | 1 | Architecture | Handles large datasets, distributed training |
| Maintenance | 1 | Ecosystem | Library maturity, update frequency, community |
| Costo infra | 2 | Pricing | GPU costs, hosting, operational expenses |

**Typical selection:** 6-7 metrics (Accuracy, Velocidad entrenamiento, Velocidad inferencia, Interpretabilidad, Datos requeridos, Robustez)

---

## Concept / Architecture

For comparing architectural patterns, design approaches, conceptual frameworks.

| Metric | Default Weight | Source Type | What to Check |
|--------|---------------|-------------|---------------|
| Relevancia | 3 | Case studies | How well it fits the problem domain |
| Factibilidad | 3 | Technical analysis | Implementation difficulty, resource requirements |
| Impacto | 2 | Evidence | Expected outcomes, performance gains |
| Coherencia | 2 | Architectural review | Internal consistency, logical soundness |
| Sostenibilidad | 2 | Long-term analysis | Maintenance burden, evolution path |
| Simplicidad | 2 | Design review | Complexity, moving parts, cognitive load |
| Comunidad | 1 | Industry adoption | Who uses it, case studies, evidence base |
| Flexibilidad | 1 | Architecture | Adaptability to change, extensibility |
| Riesgo | 2 | Risk analysis | Failure modes, migration cost, reversibility |
| Documentación | 1 | Resources | Books, articles, patterns available |

**Typical selection:** 6 metrics (Relevancia, Factibilidad, Impacto, Coherencia, Sostenibilidad, Simplicidad)

---

## Custom Domain

When no template matches, generate metrics from first principles:

1. **Identify the evaluation dimensions** — What aspects matter for this comparison?
2. **Classify each dimension** — Is it objective (measurable) or subjective (judgment-based)?
3. **Assign source types** — Where can evidence be found for each?
4. **Set initial weights** — 1 (nice-to-have), 2 (important), 3 (critical)
5. **Validate with user** — Present metrics before research begins

**Guiding questions for custom metrics:**
- What problem are you trying to solve?
- What constraints do you have (budget, time, team size)?
- What's your timeline for this decision?
- What would make this a bad choice?
- What would make this the best choice?
