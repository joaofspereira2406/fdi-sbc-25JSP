# Automotive Expert System — fdi-sbc-25JSP

A knowledge-based system for automotive reasoning, built with Python using a custom inference engine that supports forward and backward chaining over a triple-based knowledge base.

## Overview

This project implements a knowledge-based system (KBS) applied to the automotive domain. It can reason about three main tasks:

- **Task 1 — Car Diagnosis**: Detects faults, evaluates symptoms, and determines urgency levels.
- **Task 2 — Car Classification**: Classifies cars by origin, style, and type (e.g. JDM sport, muscle car, kei car).
- **Task 3 — Fuel & Efficiency**: Reasons about fuel types, emission levels, efficiency, and ecological status.

## Requirements

- Python >= 3.10
- [`uv`](https://github.com/astral-sh/uv) for dependency management

## Installation

```bash
git clone https://github.com/your-username/fdi-sbc-25JSP.git
cd fdi-sbc-25JSP
uv sync
````

## Usage

```bash
uv run -m sbc.cli
uv run -m sbc.cli --kb kb/automocion.kb
````
## CLI Commands

|Command	|   Description|
|-----------|--------------|
|descubrir!	| Run forward chaining to derive all new facts|
|<subject> <predicate> <object>.    |      Add a fact to the KB|
|no <subject> <predicate> <object>.|	Retract a fact from the KB|
| <subject> <predicate> <object>?	|Query the KB (supports variables)|
|razona si <subject> <predicate> <object>? |	Backward chaining query| 
|cargar! |	Reload the KB from disk|
|salir	| Exit the system|


### Variables

Tokens starting with an uppercase letter are treated as variables (e.g. X, Y, Coche) and will be bound during query resolution, returning a table of results.

Example Session
```bash
uv run -m sbc.cli

> descubrir!
Nuevos hechos descubiertos (145): ...

> supra es_tipo jdm_sport?
Sí (grado: 1.00)

> razona si mustang es_rival_de camaro?
Sí (grado: 0.84)

> X es_origen jdm?
┏━━━━━┳━━━━━━━━┓
┃ X   ┃ Grado  ┃
┡━━━━━╇━━━━━━━━┩
│ rx7 │  1.00  │
│ ... │  ...   │
└─────┴────────┘

> coche_A tiene_sintoma ruido_motor.
Hecho añadido: coche_A tiene_sintoma ruido_motor

> no coche_A tiene_sintoma ruido_motor.
Hecho revocado: coche_A tiene_sintoma ruido_motor

```

## Project Structure

```text
fdi-sbc-25JSP/
├── kb/
│   └── automocion.kb       # Knowledge base (facts + rules)
├── sbc/
│   ├── __init__.py
│   ├── cli.py              # CLI interface (Click + Rich)
│   ├── engine.py           # Inference engine (forward + backward chaining)
│   ├── models.py           # Data models (Triple, Rule, KnowledgeBase)
│   └── parser.py           # KB parser
├── test/
│   ├── __init__.py
│   └── test_engine.py      # Unit tests (unittest)
├── pyproject.toml
└── README.md
````

## Knowledge Base Format

Facts and rules are defined in .kb files using a Prolog-inspired syntax:



```text 
# Fact
mustang es_origen americano

# Rule with certainty degree
X es_tipo muscle_car <- X es_origen americano, X es_estilo muscle. [0.95]

# Rule with multiple conditions
X es_rival_de Y <- X es_tipo T, Y es_tipo T, X != Y. [0.84]
```

### Supported Predicates

Diagnosis: tiene_sintoma, tiene_indicador, tiene_urgencia, tiene_fallo, necesita_atencion_urgente

Classification: es_marca, es_origen, es_estilo, es_tipo, es_categoria, es_rival_de, es_alternativa_a, es_complementario_de

Fuel & Efficiency: usa_combustible, es_tipo (combustible), tiene_emision, es_eficiente_en, es_recomendado_para, es_tipo ecologico


## Running Tests

```bash
uv run python -m unittest test.test_engine
````

All 45 tests cover direct facts, forward-chained inferences, backward-chained reasoning, and negative cases across all three tasks.

### Author

João S. Pereira — Universidad Complutense de Madrid
Sistemas Basados en el Conocimiento — Convocatoria Extraordinaria 2025/26
