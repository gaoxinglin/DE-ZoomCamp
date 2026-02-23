# Module 5: Data Platforms with Bruin

## Homework Solutions

### Question 1: Bruin Pipeline Structure

**Question**: In a Bruin project, what are the required files/directories?

**Answer**: `.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/`

**Explanation**: 
The `README.md` states:
"The required parts of a Bruin project are:
- `.bruin.yml` in the root directory
- `pipeline.yml` in the `pipeline/` directory (or in the root directory if you keep everything flat)
- `assets/` folder next to `pipeline.yml` containing your Python, SQL, and YAML asset files"

### Question 2: Materialization Strategies

**Question**: You're building a pipeline that processes NYC taxi data organized by month based on `pickup_datetime`. Which materialization strategy should you use for the staging layer that deduplicates and cleans the data?

**Answer**: `time_interval`

**Explanation**:
The `README.md` best practices section states: "Staging/Reports layers: Use `time_interval` to allow re-processing specific date ranges without full refresh". Since the data is organized by month and we want to process incrementally, `time_interval` is the correct strategy.

### Question 3: Pipeline Variables

**Question**: You have the following variable defined in `pipeline.yml`:
```yaml
variables:
  taxi_types:
    type: array
    items:
      type: string
    default: ["yellow", "green"]
```
How do you override this when running the pipeline to only process yellow taxis?

**Answer**: `bruin run --var 'taxi_types=["yellow"]'`

**Explanation**:
The tutorial section mentions: "For faster testing, use `--var 'taxi_types=["yellow"]'` (skip green taxis)". Variables in Bruin can be overridden via the CLI using the `--var` flag with JSON syntax for complex types like arrays.

### Question 4: Running with Dependencies

**Question**: You've modified the `ingestion/trips.py` asset and want to run it plus all downstream assets. Which command should you use?

**Answer**: `bruin run ingestion/trips.py --downstream`

**Explanation**:
The Key Commands Reference shows: `bruin run --downstream` | Run asset and all downstream assets.
The tutorial also uses this example: `bruin run ./pipeline/assets/ingestion/trips.py ... --downstream`.

### Question 5: Quality Checks

**Question**: You want to ensure the `pickup_datetime` column in your trips table never has NULL values. Which quality check should you add to your asset definition?

**Answer**: `not_null`

**Explanation**:
The Best Practices section lists built-in checks: "Use built-in checks: `not_null`, `unique`, `positive`, `non_negative`, `accepted_values`". For preventing NULL values, `not_null` is the specific check.

### Question 6: Lineage and Dependencies

**Question**: After building your pipeline, you want to visualize the dependency graph between assets. Which Bruin command should you use?

**Answer**: `bruin lineage`

**Explanation**:
The Key Commands Reference shows: `bruin lineage <path>` | View asset dependencies.
The VS Code extension section also mentions a "Lineage Panel" and the CLI command `bruin lineage`.

### Question 7: First-Time Run

**Question**: You're running a Bruin pipeline for the first time on a new DuckDB database. What flag should you use to ensure tables are created from scratch?

**Answer**: `--full-refresh`

**Explanation**:
The tutorial advises: "First-time run tip: Use `--full-refresh` to create/replace tables from scratch (helpful on a new DuckDB file)."
Key Commands Reference: `bruin run --full-refresh` | Truncate and rebuild from scratch.
