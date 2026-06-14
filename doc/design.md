# Automotive Expert System — Technical Report

**Project:** fdi-sbc-25JSP  
**Author:** João S. Pereira  
**Course:** Sistemas Basados en el Conocimiento — Convocatoria Extraordinaria 2025/26  
**University:** Universidad Complutense de Madrid  

---

## 1. Project Description

This project implements a **knowledge-based system (KBS)** applied to the automotive domain. The system uses a triple-based knowledge representation and a custom inference engine supporting both forward and backward chaining with certainty degrees.

The system reasons over three tasks:

- **Task 1 — Car Diagnosis**: Given a set of symptoms and indicators, the system identifies faults and determines urgency levels.
- **Task 2 — Car Classification**: Classifies cars by origin, style, and type (e.g. JDM sport, muscle car, kei car, europeo familiar).
- **Task 3 — Fuel & Efficiency**: Reasons about fuel types, emission levels, efficiency contexts, and ecological status.

---

## 2. Knowledge Base Design

### 2.1 Format

The knowledge base is stored in `kb/automocion.kb` using a Prolog-inspired syntax. Each entry is either a **fact** or a **rule**.

```prolog
# Fact — subject predicate object
mustang es_origen americano

# Rule with certainty degree
X es_tipo muscle_car <- X es_origen americano, X es_estilo muscle. [0.95]

# Rule with inequality constraint
X es_rival_de Y <- X es_tipo T, Y es_tipo T, X != Y. [0.84]
````

### 2.2 Representation

All knowledge is represented as triples of the form (subject, predicate, object). Variables are tokens that start with an uppercase letter (e.g. X, Y, T). Literals are lowercase (e.g. mustang, jdm_sport).

### 2.3 Certainty Degrees

Every rule has an associated certainty degree in [0, 1]. When a rule fires, the degree of the derived fact is computed as the product of the rule's degree and the minimum degree among its premises.

### 2.4 Predicates

#### Task 1 — Diagnosis:

| Predicate                   | Description                                 |
| --------------------------- | ------------------------------------------- |
| `tiene_sintoma`             | Car exhibits a symptom.                     |
| `indica`           | Car has a dashboard indicator active.       |
| `tiene_urgencia`            | Symptom or indicator has an urgency level.  |
| `tiene_fallo`               | Derived fault inferred from symptoms.       |
|`es_fallo_probable`| Derived Urgent defect present in the car.|
| `necesita_atencion_urgente` | Derived critical urgency condition.         |



----

#### Task 2 — Classification:
| Predicate              | Description                                                      |
| ---------------------- | ---------------------------------------------------------------- |
| `es_marca`             | Brand of the car.                                                |
| `es_origen`            | Geographic origin (`jdm`, `americano`, `europeo`).               |
| `es_estilo`            | Body/driving style (`sport`, `muscle`, `familiar`, `kei`, `pickup`). |
| `es_tipo`              | Derived classification (`jdm_sport`, `muscle_car`, etc.).        |
| `es_categoria`         | Derived category (`premium`, `coleccion`, `contaminante`).       |
| `es_rival_de`          | Derived rivalry between cars of the same type.                   |
| `es_alternativa_a`     | Derived alternative relationship between cars of the same type.  |
| `es_complementario_de` | Derived complementary relationship between cars of different types. |

#### Task 3 — Fuel & Efficiency

| Predicate              | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `usa_combustible`      | Fuel type used by a car.                                                   |
| `es_clase`             | Maps fuel types to categories (e.g., `combustible_fosil`, `combustible_limpio`). |
| `tiene_emision`        | Emission level derived from fuel class (`alta`, `media`, `nula`).          |
| `es_eficiente_en`      | Efficiency context based on fuel type (e.g., `ciudad`, `autopista`).       |
| `es_recomendado_para`  | Final usage recommendation (e.g., `ciudad`, `viaje_largo`).                |
| `es_categoria`         | Derived classification (e.g., `ecologico`, `contaminante`).                |

## 3. System Architecture
```text
fdi-sbc-25JSP/
├── kb/
│   └── automocion.kb       # Knowledge base
├── sbc/
│   ├── __init__.py
│   ├── models.py           # Data models
│   ├── parser.py           # KB parser
│   ├── engine.py           # Inference engine
│   └── cli.py              # CLI interface
├── test/
│   ├── __init__.py
│   └── test_engine.py      # Unit tests
├── pyproject.toml
└── README.md
````
 
### 3.1 `sbc/models.py`

Defines the core data structures:

- **`Triple`** — Immutable named tuple (`subject`, `predicate`, `obj`) representing a fact.
- **`Rule`** — Contains a head (`Triple`), a list of body conditions (`Triple`s), a list of constraints (inequality checks), and a certainty degree (`float`).
- **`KnowledgeBase`** — Stores a collection of facts (`Triple`s with associated degrees) and a list of inference rules.

### 3.2 `sbc/parser.py`

Parses `.kb` files line by line:

- Lines containing `←` (`<-`) are interpreted as rules.
  - The rule head is parsed as a `Triple`.
  - The rule body is parsed as a comma-separated list of `Triple` conditions.
  - An optional certainty degree can be specified using a `[degree]` suffix.
- Lines without `←` (`<-`) are interpreted as facts and assigned a default degree of `1.0`.
- Comments (`#`) and blank lines are ignored during parsing.

### 3.3 `sbc/engine.py`

Implements the inference engine and its three main reasoning mechanisms:

#### Query

Matches a goal `Triple` against the facts stored in the knowledge base using unification.

- Variables are bound to matching values.
- Returns a list of `(bindings, degree)` pairs representing all valid matches and their certainty degrees.

#### Forward Chaining

Performs data-driven inference by repeatedly applying rules whose body conditions are satisfied by the current set of facts.

- Evaluates all applicable rules.
- Derives and inserts new facts into the knowledge base.
- Continues until no additional facts can be inferred (fixpoint).
- Returns the list of newly derived facts.

#### Backward Chaining

Performs goal-driven inference by recursively attempting to prove a target fact.

1. Tries to match the goal directly against known facts.
2. Searches for rules whose head unifies with the goal.
3. Recursively proves each condition in the rule body.
4. Verifies inequality constraints (e.g., `X != Y`) after all relevant variables have been bound.

This process continues until the goal is proven or no valid proof path remains.


### 3.4 `sbc/cli.py`

Provides an interactive REPL built with **Click** and **Rich**.

- **Variable queries** return a Rich-formatted table with:
  - One column per bound variable
  - A `degree` column showing certainty
- **Ground queries** (no variables) return `Sí` or `No` with a certainty degree
- The `descubrir!` command runs forward chaining and prints all derived facts in a table
- Forward chaining is also executed automatically at startup so the KB is fully saturated before queries

---

## 4. Inference Examples

### Task 1 — Fault Diagnosis

```text
> coche_A tiene_sintoma humo_negro.
Hecho añadido: coche_A tiene_sintoma humo_negro

> descubrir!
...
│ coche_A │ tiene_fallo │ fallo_motor │
...

> razona si coche_A necesita_atencion_urgente critica?
Sí (grado: 0.81)
```

---

### Task 2 — Classification

```text
> razona si supra es_tipo jdm_sport?
Sí (grado: 1.00)

> X es_tipo muscle_car?
┏━━━━━━━━━┳━━━━━━━┓
┃ X       ┃ Grado ┃
┡━━━━━━━━━╇━━━━━━━┩
│ mustang │ 1.00  │
│ camaro  │ 1.00  │
└─────────┴───────┘

> razona si mustang es_rival_de camaro?
Sí (grado: 0.84)
```

---

### Task 3 — Fuel & Efficiency

```text
> X es_tipo_ecologico?
┏━━━━━━━┳━━━━━━━┓
┃ X     ┃ Grado ┃
┡━━━━━━━╇━━━━━━━┩
│ tesla │ 0.90  │
│ prius │ 0.85  │
└───────┴───────┘

> razona si tesla es_recomendado_para ciudad?
Sí (grado: 0.92)
```

---

## 5. Test Coverage

Tests are located in `test/test_engine.py` and use Python’s built-in `unittest` module.

```bash
uv run python -m unittest test.test_engine
```

### Coverage Summary

| Test Class                     | Coverage |
|------------------------------|----------|
| TestDiagnosticoHechos        | Direct symptom, indicator, and urgency facts |
| TestDiagnosticoDerivados     | Derived faults and critical urgency via forward/backward chaining |
| TestClasificacionHechos      | Brand, origin, and style direct facts |
| TestClasificacionDerivados   | 8 car-type classifications, category derivations, no cross-contamination |
| TestCombustibleHechos        | Fuel type facts and fuel category facts |
| TestCombustibleDerivados     | Emission levels, efficiency, ecological status, long-trip recommendations |
| TestRestriccionesDerivados   | Rivals, alternatives, complementary relations, no self-references |

---

```text
Total: 50 tests — all passing.
```

## 6. Design Decisions

- **Triple-based representation** was chosen for its simplicity and flexibility. Any relation can be expressed as a `(subject, predicate, object)` structure without requiring schema changes.

- **Certainty degrees** allow the system to express confidence in derived knowledge. This is especially useful in diagnostic tasks where symptoms can be ambiguous or partially reliable.

- The **uppercase = variable convention** follows Prolog-style logic programming, making the knowledge base syntax intuitive for rule-based reasoning.

- **Forward chaining on startup** ensures that all derivable facts are computed immediately when the system launches, eliminating the need to manually run `descubrir!` before querying.

- **Rich table output for variable queries** improves readability compared to raw dictionary or tuple-based bindings, making inference results easier to interpret.
