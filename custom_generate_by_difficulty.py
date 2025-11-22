"""Generate mathematics dataset with difficulty level control."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import random
import sys
from absl import app
from absl import flags
from mathematics_dataset.modules import modules
import six

FLAGS = flags.FLAGS

# Define our custom flags
flags.DEFINE_string('filter', '', 'Restrict to matching module names')
flags.DEFINE_integer('count', 10, 'Number of questions to generate')
flags.DEFINE_enum('difficulty', 'easy', ['easy', 'medium', 'hard', 'mixed'],
                  'Difficulty level: easy, medium, hard, or mixed')
flags.DEFINE_string('entropy_range', '', 'Custom entropy range as "min,max" (e.g., "5.0,7.5"). Overrides difficulty.')
flags.DEFINE_boolean('show_dropped', False, 'Whether to print dropped samples')
flags.DEFINE_boolean('test_entropy', False, 'Test entropy function and exit')
flags.DEFINE_boolean('show_entropy', False, 'Show entropy range for each question')
flags.DEFINE_boolean('list_modules', False, 'List all available modules and exit')

_MODULES = []


def _make_custom_entropy_fn(min_val, max_val):
  """Create entropy function with custom range."""
  def modify_entropy(range_):
    assert len(range_) == 2
    length = range_[1] - range_[0]
    # Map the custom range proportionally to the given range
    lower_fraction = min_val / 10.0  # Assume max entropy is 10
    upper_fraction = max_val / 10.0
    return (range_[0] + lower_fraction * length, range_[0] + upper_fraction * length)
  
  return modify_entropy


def _make_entropy_fn(level, num_levels):
  """Create entropy function for specific difficulty level."""
  lower = level / num_levels
  upper = (level + 1) / num_levels
  
  def modify_entropy(range_):
    assert len(range_) == 2
    length = range_[1] - range_[0]
    result = (range_[0] + lower * length, range_[0] + upper * length)
    return result
  
  return modify_entropy


def _flatten_modules(modules_dict, prefix=''):
  """Recursively flatten nested module dictionary."""
  result = {}
  for name, value in six.iteritems(modules_dict):
    full_name = f"{prefix}__{name}" if prefix else name
    if callable(value):
      result[full_name] = value
    elif isinstance(value, dict):
      result.update(_flatten_modules(value, full_name))
  return result


def init_modules(filter_by, entropy_fn):
  """Initialize modules and create sample function."""
  global _MODULES
  
  # Get all training modules with the specified entropy function
  all_modules_nested = modules.train(entropy_fn)
  
  # Flatten the nested structure
  all_modules = _flatten_modules(all_modules_nested)
  
  _MODULES = []
  for name, module in six.iteritems(all_modules):
    if filter_by and not re.match(filter_by, name):
      continue
    _MODULES.append((name, module))
  
  if not _MODULES:
    sample_names = sorted(all_modules.keys())[:10]
    print(f'ERROR: No modules matched filter "{filter_by}". Sample modules: {", ".join(sample_names)}', file=sys.stderr)
    sys.exit(1)


def sample_from_module():
  """Sample problem from random module."""
  if not _MODULES:
    return None
  name, module = _MODULES[random.randint(0, len(_MODULES) - 1)]
  try:
    return module()
  except Exception:
    return None


def main(unused_argv):
  """Generate questions with specified difficulty."""
  
  # List modules mode - show all available modules and exit
  if FLAGS.list_modules:
    # Use a dummy entropy function to get module list
    dummy_entropy = _make_entropy_fn(0, 1)
    all_modules_nested = modules.train(dummy_entropy)
    all_modules = _flatten_modules(all_modules_nested)
    
    print(f"Available modules ({len(all_modules)} total):")
    print("=" * 60)
    
    # Group by category
    categories = {}
    for name in sorted(all_modules.keys()):
      category = name.split('__')[0]
      if category not in categories:
        categories[category] = []
      categories[category].append(name)
    
    for category in sorted(categories.keys()):
      print(f"\n{category.upper()} ({len(categories[category])} modules):")
      for module_name in categories[category]:
        print(f"  - {module_name}")
    
    print("\n" + "=" * 60)
    print("Usage examples:")
    print(f"  --filter=algebra__linear_1d           (exact match)")
    print(f"  --filter=algebra                      (all algebra)")
    print(f'  --filter="algebra__.*"                (regex: all algebra)')
    print(f'  --filter=".*linear.*"                 (regex: all with linear)')
    print(f'  --filter="calculus__.*|algebra__.*"   (regex: calculus OR algebra)')
    return
  
  # Test mode - show entropy ranges and exit
  if FLAGS.test_entropy:
    print("Testing entropy functions with range (0, 10):")
    print("=" * 50)
    test_range = (0, 10)
    
    for level_name, level_num in [('easy', 0), ('medium', 1), ('hard', 2)]:
      entropy_fn = _make_entropy_fn(level_num, 3)
      result = entropy_fn(test_range)
      print(f"{level_name.upper():8s}: {result[0]:.2f} to {result[1]:.2f}")
    
    print("\nThis means:")
    print("  Easy:   uses lower 1/3 of complexity (simpler parameters)")
    print("  Medium: uses middle 1/3 of complexity (moderate parameters)")
    print("  Hard:   uses upper 1/3 of complexity (complex parameters)")
    print("\nEntropy controls things like:")
    print("  - Coefficient sizes")
    print("  - Polynomial degrees")
    print("  - Number of operations/steps")
    print("  - Complexity of intermediate calculations")
    print("\nYou can also use custom entropy ranges:")
    print("  --entropy_range='2.5,5.0' (slightly easier than medium)")
    print("  --entropy_range='8.0,10.0' (very hard)")
    print("  --entropy_range='0.0,10.0' (full range)")
    return
  
  # Determine entropy function
  if FLAGS.entropy_range:
    # Parse custom entropy range
    try:
      parts = FLAGS.entropy_range.split(',')
      if len(parts) != 2:
        print(f'ERROR: entropy_range must be "min,max" format (e.g., "5.0,7.5")', file=sys.stderr)
        sys.exit(1)
      min_entropy = float(parts[0])
      max_entropy = float(parts[1])
      if min_entropy < 0 or max_entropy > 10 or min_entropy >= max_entropy:
        print(f'ERROR: entropy values must be between 0 and 10, with min < max', file=sys.stderr)
        sys.exit(1)
      entropy_fn = _make_custom_entropy_fn(min_entropy, max_entropy)
      difficulty_label = f"custom ({min_entropy:.1f}-{max_entropy:.1f})"
    except ValueError as e:
      print(f'ERROR: Invalid entropy_range format: {e}', file=sys.stderr)
      sys.exit(1)
  else:
    # Map difficulty to entropy function
    difficulty_map = {
        'easy': _make_entropy_fn(0, 3),
        'medium': _make_entropy_fn(1, 3),
        'hard': _make_entropy_fn(2, 3),
        'mixed': _make_entropy_fn(0, 1)  # Full range
    }
    entropy_fn = difficulty_map[FLAGS.difficulty]
    difficulty_label = FLAGS.difficulty
  
  # Initialize modules
  init_modules(FLAGS.filter, entropy_fn)
  
  generated_count = 0
  dropped_count = 0
  
  for _ in range(FLAGS.count * 100):  # Over-generate to account for drops
    if generated_count >= FLAGS.count:
      break
      
    problem = sample_from_module()
    
    if problem is None:
      dropped_count += 1
      continue
    
    # Show difficulty level info if requested
    if FLAGS.show_entropy:
      test_range = (0, 10)
      entropy_result = entropy_fn(test_range)
      print(f"[DIFFICULTY: {difficulty_label} | ENTROPY RANGE: {entropy_result[0]:.2f} to {entropy_result[1]:.2f}]", file=sys.stderr)
    
    # Print in standard format: question on one line, answer on next
    print(problem.question)
    print(problem.answer)
    generated_count += 1
  
  if generated_count < FLAGS.count:
    print(f'WARNING: Only generated {generated_count} out of {FLAGS.count} requested', file=sys.stderr)


if __name__ == '__main__':
  app.run(main)
