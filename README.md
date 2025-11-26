# Red Scare

This project answers the five “Red Scare!” graph questions on the instances in `data/`.

## Requirements
- Python 3.8+ (only standard library modules used)

## Run on a single instance
From the repository root:
```sh
python3 src/red_scare.py data/G-ex.txt
```
This prints the graph header and the answers for:
`None` (shortest s–t path avoiding internal red), `Some` (path with ≥1 red), `Many`, `Few`, and `Alternate`.  
`Many` returns `None` when the instance is outside the supported class (purely directed DAGs); `Alternate` returns `None` when the instance has any directed edges. In those cases the CLI shows `?!`.

## Recreate `results.txt` for all instances
Run the batch script from the project root:
```sh
python3 src/run_all.py > results.txt
```
The output is tab-separated with columns:
`instance_name`, `n`, `A` (Alternate), `F` (Few), `M` (Many), `N` (None), `S` (Some).
When a solver declines an instance (`Many` on non-DAGs; `Alternate` on graphs with directed edges), the value is `?!`.
