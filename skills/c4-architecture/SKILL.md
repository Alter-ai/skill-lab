---
name: c4-architecture
description: Generate architecture documentation using C4 model Mermaid diagrams. Use when asked to create architecture diagrams, document system architecture, visualize software structure, create C4 diagrams, or generate context/container/component/deployment diagrams. Triggers include "architecture diagram", "C4 diagram", "system context", "container diagram", "component diagram", "deployment diagram", "document architecture", "visualize architecture".
---

# C4 Architecture Documentation

Generate software architecture documentation using C4 model diagrams in Mermaid syntax.

## Workflow

1. **Understand scope** - Determine which C4 level(s) are needed based on audience
2. **Analyze codebase** - Explore the system to identify components, containers, and relationships
3. **Generate diagrams** - Create Mermaid C4 diagrams at appropriate abstraction levels
4. **Document** - Write all diagrams, their descriptions and the AI YAML into one `ARCHITECTURE.md` (see [Output Format](#output-format))
5. **Cross-check** - Every Mermaid alias has a YAML element with the same `id`, and every `Rel` has a YAML relation, and vice versa

## C4 Diagram Levels

Select the appropriate level based on the documentation need:

| Level | Diagram Type | Audience | Shows | When to Create |
|-------|-------------|----------|-------|----------------|
| 1 | **C4Context** | Everyone | System + external actors | Always (required) |
| 2 | **C4Container** | Technical | Apps, databases, services | Always (required) |
| 3 | **C4Component** | Developers | Internal components | Only if adds value |
| 4 | **C4Deployment** | DevOps | Infrastructure nodes | For production systems |
| - | **C4Dynamic** | Technical | Request flows (numbered) | For complex workflows |

**Key Insight:** "Context + Container diagrams are sufficient for most software development teams." Only create Component/Code diagrams when they genuinely add value.

## Quick Start Examples

### System Context (Level 1)
```mermaid
C4Context
  title System Context - Workout Tracker

  Person(user, "User", "Tracks workouts and exercises")
  System(app, "Workout Tracker", "Vue PWA for tracking strength and CrossFit workouts")
  System_Ext(browser, "Web Browser", "Stores data in IndexedDB")

  Rel(user, app, "Uses")
  Rel(app, browser, "Persists data to", "IndexedDB")
```

### Container Diagram (Level 2)
```mermaid
C4Container
  title Container Diagram - Workout Tracker

  Person(user, "User", "Tracks workouts")

  Container_Boundary(app, "Workout Tracker PWA") {
    Container(spa, "SPA", "Vue 3, TypeScript", "Single-page application")
    Container(pinia, "State Management", "Pinia", "Manages application state")
    ContainerDb(indexeddb, "IndexedDB", "Dexie", "Local workout storage")
  }

  Rel(user, spa, "Uses")
  Rel(spa, pinia, "Reads/writes state")
  Rel(pinia, indexeddb, "Persists", "Dexie ORM")
```

### Component Diagram (Level 3)
```mermaid
C4Component
  title Component Diagram - Workout Feature

  Container(views, "Views", "Vue Router pages")

  Container_Boundary(workout, "Workout Feature") {
    Component(useWorkout, "useWorkout", "Composable", "Workout execution state")
    Component(useTimer, "useTimer", "Composable", "Timer state machine")
    Component(workoutRepo, "WorkoutRepository", "Dexie", "Workout persistence")
  }

  Rel(views, useWorkout, "Uses")
  Rel(useWorkout, useTimer, "Controls")
  Rel(useWorkout, workoutRepo, "Saves to")
```

### Dynamic Diagram (Request Flow)
```mermaid
C4Dynamic
  title Dynamic Diagram - User Sign In Flow

  ContainerDb(db, "Database", "PostgreSQL", "User credentials")
  Container(spa, "Single-Page App", "React", "Banking UI")

  Container_Boundary(api, "API Application") {
    Component(signIn, "Sign In Controller", "Express", "Auth endpoint")
    Component(security, "Security Service", "JWT", "Validates credentials")
  }

  Rel(spa, signIn, "1. Submit credentials", "JSON/HTTPS")
  Rel(signIn, security, "2. Validate")
  Rel(security, db, "3. Query user", "SQL")

  UpdateRelStyle(spa, signIn, $textColor="blue", $offsetY="-30")
```

### Deployment Diagram
```mermaid
C4Deployment
  title Deployment Diagram - Production

  Deployment_Node(browser, "Customer Browser", "Chrome/Firefox") {
    Container(spa, "SPA", "React", "Web application")
  }

  Deployment_Node(aws, "AWS Cloud", "us-east-1") {
    Deployment_Node(ecs, "ECS Cluster", "Fargate") {
      Container(api, "API Service", "Node.js", "REST API")
    }
    Deployment_Node(rds, "RDS", "db.r5.large") {
      ContainerDb(db, "Database", "PostgreSQL", "Application data")
    }
  }

  Rel(spa, api, "API calls", "HTTPS")
  Rel(api, db, "Reads/writes", "JDBC")
```

## Element Syntax

### People and Systems
```
Person(alias, "Label", "Description")
Person_Ext(alias, "Label", "Description")       # External person
System(alias, "Label", "Description")
System_Ext(alias, "Label", "Description")       # External system
SystemDb(alias, "Label", "Description")         # Database system
SystemQueue(alias, "Label", "Description")      # Queue system
```

### Containers
```
Container(alias, "Label", "Technology", "Description")
Container_Ext(alias, "Label", "Technology", "Description")
ContainerDb(alias, "Label", "Technology", "Description")
ContainerQueue(alias, "Label", "Technology", "Description")
```

### Components
```
Component(alias, "Label", "Technology", "Description")
Component_Ext(alias, "Label", "Technology", "Description")
ComponentDb(alias, "Label", "Technology", "Description")
```

### Boundaries
```
Enterprise_Boundary(alias, "Label") { ... }
System_Boundary(alias, "Label") { ... }
Container_Boundary(alias, "Label") { ... }
Boundary(alias, "Label", "type") { ... }
```

### Relationships
```
Rel(from, to, "Label")
Rel(from, to, "Label", "Technology")
BiRel(from, to, "Label")                        # Bidirectional
Rel_U(from, to, "Label")                        # Upward
Rel_D(from, to, "Label")                        # Downward
Rel_L(from, to, "Label")                        # Leftward
Rel_R(from, to, "Label")                        # Rightward
```

### Deployment Nodes
```
Deployment_Node(alias, "Label", "Type", "Description") { ... }
Node(alias, "Label", "Type", "Description") { ... }  # Shorthand
```

## Styling and Layout

### Layout Configuration
```
UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```
- `$c4ShapeInRow` - Number of shapes per row (default: 4)
- `$c4BoundaryInRow` - Number of boundaries per row (default: 2)

### Element Styling
```
UpdateElementStyle(alias, $fontColor="red", $bgColor="grey", $borderColor="red")
```

### Relationship Styling
```
UpdateRelStyle(from, to, $textColor="blue", $lineColor="blue", $offsetX="5", $offsetY="-10")
```
Use `$offsetX` and `$offsetY` to fix overlapping relationship labels.

## Best Practices

### Essential Rules

1. **Every element must have**: Name, Type, Technology (where applicable), and Description
2. **Use unidirectional arrows only** - Bidirectional arrows create ambiguity
3. **Label arrows with action verbs** - "Sends email using", "Reads from", not just "uses"
4. **Include technology labels** - "JSON/HTTPS", "JDBC", "gRPC"
5. **Stay under 20 elements per diagram** - Split complex systems into multiple diagrams

### Clarity Guidelines

1. **Start at Level 1** - Context diagrams help frame the system scope
2. **One level per section** - Each diagram stays on a single abstraction level, in its own section of `ARCHITECTURE.md`
3. **Meaningful aliases** - Use descriptive aliases (e.g., `orderService` not `s1`)
4. **Concise descriptions** - Keep descriptions under 50 characters when possible
5. **Always include a title** - "System Context diagram for [System Name]"

### What to Avoid

See [references/common-mistakes.md](references/common-mistakes.md) for detailed anti-patterns:
- Confusing containers (deployable) vs components (non-deployable)
- Modeling shared libraries as containers
- Showing message brokers as single containers instead of individual topics
- Adding undefined abstraction levels like "subcomponents"
- Removing type labels to "simplify" diagrams

## Microservices Guidelines

### Single Team Ownership
Model each microservice as a **container** (or container group):
```mermaid
C4Container
  title Microservices - Single Team

  System_Boundary(platform, "E-commerce Platform") {
    Container(orderApi, "Order Service", "Spring Boot", "Order processing")
    ContainerDb(orderDb, "Order DB", "PostgreSQL", "Order data")
    Container(inventoryApi, "Inventory Service", "Node.js", "Stock management")
    ContainerDb(inventoryDb, "Inventory DB", "MongoDB", "Stock data")
  }
```

### Multi-Team Ownership
Promote microservices to **software systems** when owned by separate teams:
```mermaid
C4Context
  title Microservices - Multi-Team

  Person(customer, "Customer", "Places orders")
  System(orderSystem, "Order System", "Team Alpha")
  System(inventorySystem, "Inventory System", "Team Beta")
  System(paymentSystem, "Payment System", "Team Gamma")

  Rel(customer, orderSystem, "Places orders")
  Rel(orderSystem, inventorySystem, "Checks stock")
  Rel(orderSystem, paymentSystem, "Processes payment")
```

### Event-Driven Architecture
Show individual topics/queues as containers, NOT a single "Kafka" box:
```mermaid
C4Container
  title Event-Driven Architecture

  Container(orderService, "Order Service", "Java", "Creates orders")
  Container(stockService, "Stock Service", "Java", "Manages inventory")
  ContainerQueue(orderTopic, "order.created", "Kafka", "Order events")
  ContainerQueue(stockTopic, "stock.reserved", "Kafka", "Stock events")

  Rel(orderService, orderTopic, "Publishes to")
  Rel(stockService, orderTopic, "Subscribes to")
  Rel(stockService, stockTopic, "Publishes to")
  Rel(orderService, stockTopic, "Subscribes to")
```

## Output Format

Write **one file**, `docs/architecture/ARCHITECTURE.md`, readable by humans and by other people's AI agents:

- **Humans** read the rendered Mermaid diagrams and the descriptions.
- **AI** reads the Mermaid source and the YAML at the end. The YAML is the source of truth: if a diagram and the YAML disagree, the YAML wins.

Template (include only the levels the audience needs; Context and Container are required):

````markdown
# <System> Architecture

## How to read this
Humans: diagrams and descriptions below. AI agents: the YAML in "AI structured data" lists every element and relation and is authoritative; `id` equals the Mermaid alias.

## 1. System Context
```mermaid
C4Context
  title System Context - <System>
  ...
```
**Scope:** what this diagram covers and what it deliberately leaves out.
**Key decisions:** short bullets, link ADRs (`docs/decisions/001-....md`).

## 2. Container
```mermaid
C4Container
  ...
```
**Scope:** ...
**Key decisions:** ...

## 3. Component - <feature>   (optional; also Deployment / Dynamic sections as needed)

## AI structured data
```yaml
elements:
  - id: api                # same as Mermaid alias, unique across all levels
    level: container       # context | container | component | deployment
    type: container        # person | system | system_ext | container | container_db | container_queue | component | node
    name: API
    tech: Node.js
    description: REST API for orders
    code: src/server/      # repo path; omit for external systems and people
    parent: shop           # optional: enclosing system/container/node id
relations:
  - from: web
    to: api
    label: Creates orders
    protocol: HTTPS/JSON
```
````

Rules:
- One element appears **once** in the YAML even if it shows up in several diagrams; reuse the same alias in every diagram.
- Every `Rel` in any diagram has a matching YAML relation (same `from`, `to`, `label`); nothing in the YAML is missing from the diagrams.
- Point the repo's `CLAUDE.md` / `AGENTS.md` at the file: "Architecture: read `docs/architecture/ARCHITECTURE.md`."

## Exporting Images (for Word or slides)

Render every diagram in the file to PNG next to it (`ARCHITECTURE-1.png`, `ARCHITECTURE-2.png`, ... in file order; a file with one diagram gives `ARCHITECTURE.png`):

```bash
bash scripts/render.sh <repo>/docs/architecture/ARCHITECTURE.md
```

The script uses the Mermaid CLI pinned at `~/.local/mermaid-cli` (11.17.0, with its own Chromium). Then open the PNG and look at it: Mermaid's C4 auto-layout often overlaps relationship labels. Fix with short labels and `UpdateRelStyle(from, to, $offsetX=..., $offsetY=...)` per relationship, re-render, and look again. On 11.17.0, `UpdateLayoutConfig($c4ShapeInRow=...)` did not change the column count.

## Audience-Appropriate Detail

| Audience | Recommended Diagrams |
|----------|---------------------|
| Executives | System Context only |
| Product Managers | Context + Container |
| Architects | Context + Container + key Components |
| Developers | All levels as needed |
| DevOps | Container + Deployment |

## References

- [references/c4-syntax.md](references/c4-syntax.md) - Complete Mermaid C4 syntax
- [references/common-mistakes.md](references/common-mistakes.md) - Anti-patterns to avoid
- [references/advanced-patterns.md](references/advanced-patterns.md) - Microservices, event-driven, deployment
