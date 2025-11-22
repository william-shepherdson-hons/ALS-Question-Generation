# Mathematics Dataset Generator with Difficulty Control

A custom question generator built on top of Google DeepMind's [mathematics_dataset](https://github.com/google-deepmind/mathematics_dataset) that provides fine-grained control over question difficulty, complexity, and type.

## Credits

This project extends the original [Mathematics Dataset](https://github.com/google-deepmind/mathematics_dataset) by Google DeepMind:

> **Original Paper:** [Analysing Mathematical Reasoning Abilities of Neural Models](https://openreview.net/pdf?id=H1gR5iR5FX) (Saxton, Grefenstette, Hill, Kohli)
>
> **Original Repository:** https://github.com/google-deepmind/mathematics_dataset

All question generation logic and mathematical modules are from the original repository. This project adds a custom interface for controlling difficulty levels through entropy functions.

## Features

**Difficulty Control** - Generate questions at specific difficulty levels (easy, medium, hard)

**Custom Entropy Ranges** - Fine-tune complexity with precise entropy values (0.0-10.0)

**Module Filtering** - Target specific math topics (algebra, calculus, arithmetic, etc.)

**Exact Question Counts** - Generate exactly the number of questions you need

**Dockerized** - Consistent environment with all dependencies included

## Quick Start

### Build the Docker Image

```bash
docker build -t math-dataset .
```

### Generate Questions

```bash
# Easy algebra questions
docker run math-dataset python -m mathematics_dataset.custom_generate_by_difficulty \
  --filter=algebra__linear_1d \
  --difficulty=easy \
  --count=10

# Hard calculus questions
docker run math-dataset python -m mathematics_dataset.custom_generate_by_difficulty \
  --filter=calculus__differentiate \
  --difficulty=hard \
  --count=5

# Custom entropy range (very precise control)
docker run math-dataset python -m mathematics_dataset.custom_generate_by_difficulty \
  --filter=algebra__polynomial_roots \
  --entropy_range="7.5,9.0" \
  --count=10
```

## Usage

### List Available Modules

```bash
docker run math-dataset python -m mathematics_dataset.custom_generate_by_difficulty \
  --list_modules
```

This shows all 56 available modules grouped by category:
- **algebra** - linear equations, polynomial roots, sequences
- **arithmetic** - addition, multiplication, division, surds
- **calculus** - differentiation
- **comparison** - sorting, closest numbers
- **measurement** - unit conversion, time
- **numbers** - divisibility, primes, place value, rounding
- **polynomials** - expansion, composition, evaluation
- **probability** - sampling without replacement

### Difficulty Levels

**Preset Difficulties:**
```bash
--difficulty=easy     # Uses entropy range 0.0-3.33 (lower third)
--difficulty=medium   # Uses entropy range 3.33-6.67 (middle third)
--difficulty=hard     # Uses entropy range 6.67-10.0 (upper third)
--difficulty=mixed    # Uses full entropy range 0.0-10.0
```

**Custom Entropy (Advanced):**
```bash
# Ultra easy (simpler than easy preset)
--entropy_range="0.0,2.0"

# Between easy and medium
--entropy_range="2.5,5.0"

# Between medium and hard
--entropy_range="6.0,8.0"

# Extremely hard
--entropy_range="9.0,10.0"

# Very narrow range for consistent difficulty
--entropy_range="5.0,5.2"
```

### Filtering Modules

```bash
# Exact module name
--filter=algebra__linear_1d

# All modules in a category
--filter=algebra

# Regex patterns (use quotes)
--filter="algebra__.*"                    # All algebra
--filter=".*linear.*"                     # Anything with "linear"
--filter="calculus__.*|arithmetic__.*"    # Calculus OR arithmetic
```

### Additional Flags

```bash
--count=N              # Generate exactly N questions
--show_entropy         # Display entropy range for each question
--test_entropy         # Test entropy function and exit (no generation)
--list_modules         # List all available modules and exit
```

## Examples

### Generate Training Dataset by Difficulty

```bash
# 100 easy linear algebra problems
docker run math-dataset python -m mathematics_dataset.custom_generate_by_difficulty \
  --filter=algebra__linear_1d \
  --difficulty=easy \
  --count=100 > easy_algebra.txt

# 100 medium linear algebra problems
docker run math-dataset python -m mathematics_dataset.custom_generate_by_difficulty \
  --filter=algebra__linear_1d \
  --difficulty=medium \
  --count=100 > medium_algebra.txt

# 100 hard linear algebra problems
docker run math-dataset python -m mathematics_dataset.custom_generate_by_difficulty \
  --filter=algebra__linear_1d \
  --difficulty=hard \
  --count=100 > hard_algebra.txt
```

### Compare Difficulty Levels

```bash
# See the difference in complexity
docker run math-dataset python -m mathematics_dataset.custom_generate_by_difficulty \
  --filter=algebra__polynomial_roots \
  --difficulty=easy \
  --count=3 \
  --show_entropy

docker run math-dataset python -m mathematics_dataset.custom_generate_by_difficulty \
  --filter=algebra__polynomial_roots \
  --difficulty=hard \
  --count=3 \
  --show_entropy
```

### Generate Mixed Topic Dataset

```bash
# All algebra types at medium difficulty
docker run math-dataset python -m mathematics_dataset.custom_generate_by_difficulty \
  --filter="algebra__.*" \
  --difficulty=medium \
  --count=50 > mixed_algebra.txt
```

## Output Format

Questions and answers are printed on alternating lines:

```
Solve 3*x + 5 = 20 for x.
5
Factor 2*m**2 + 8*m + 6.
2*(m + 1)*(m + 3)
```

## Understanding Entropy

**Entropy** controls the complexity of questions by affecting:
- Coefficient sizes (larger numbers at higher entropy)
- Polynomial degrees (higher degrees at higher entropy)
- Number of operations/steps required
- Complexity of intermediate calculations

**Examples of entropy impact:**

| Entropy Range | Polynomial Roots Example |
|--------------|--------------------------|
| 0.0 - 2.0 | `Factor 2*x**2 + 4*x + 2` → `2*(x + 1)**2` |
| 3.0 - 5.0 | `Factor x**3 - 7*x**2 + 14*x - 8` → `(x - 1)(x - 2)(x - 4)` |
| 8.0 - 10.0 | `Factor 2*m**5 + 444130*m**4 + ...` → `2*(m - 1)*(m + 111029)**2/11` |

## Interactive Shell

For exploratory use, you can open a bash shell in the container:

```bash
docker run -it math-dataset /bin/bash

# Inside the container:
python -m mathematics_dataset.custom_generate_by_difficulty --list_modules
python -m mathematics_dataset.custom_generate_by_difficulty --filter=calculus --difficulty=hard --count=5
```



## Requirements

- Docker
- No other dependencies (everything runs in container)

## Technical Details

### How Difficulty Works

The original mathematics_dataset uses entropy functions to control question generation. This project exposes that functionality:

1. **Entropy Function**: Maps a complexity range (0-10) to a subset based on difficulty
2. **Easy**: Uses lower third (0.0-3.33) → simpler parameters
3. **Medium**: Uses middle third (3.33-6.67) → moderate parameters  
4. **Hard**: Uses upper third (6.67-10.0) → complex parameters

The entropy function is passed to each module's generator, which uses it to determine parameter values like coefficient sizes, polynomial degrees, and number of operations.

### Module Structure

Modules are organized hierarchically:
```
algebra
  ├── linear_1d              (single-variable linear equations)
  ├── linear_1d_composed     (composed linear equations)
  ├── linear_2d              (two-variable systems)
  ├── polynomial_roots       (factoring and root-finding)
  └── sequence_*             (sequence problems)
```

The custom generator flattens this structure to `category__subcategory` format for easy filtering.

## Troubleshooting

### No questions generated
- Check that your filter matches available modules with `--list_modules`
- Try a less restrictive filter or different module name

### Questions all seem the same difficulty
- Linear equations (`linear_1d`) have narrow complexity range by nature
- Try modules with wider complexity like `polynomial_roots` or `differentiate`
- Use `--show_entropy` to verify entropy ranges are being applied

### Docker build fails
- Ensure you have the `custom_generate_by_difficulty.py` file in the same directory as the Dockerfile
- Check Docker has enough disk space


## Acknowledgments

- Google DeepMind for creating the original mathematics_dataset
- The original paper authors: Saxton, Grefenstette, Hill, and Kohli