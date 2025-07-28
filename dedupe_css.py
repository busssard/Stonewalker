import re
from collections import defaultdict

CSS_FILE = 'source/content/assets/css/styles.css'
OUTPUT_FILE = 'source/content/assets/css/styles.deduped.css'


def normalize_css_block(block_lines):
    """
    Normalize a CSS block for comparison: remove whitespace and comments.
    """
    block = '\n'.join(block_lines)
    # Remove comments
    block = re.sub(r'/\*.*?\*/', '', block, flags=re.DOTALL)
    # Remove whitespace
    block = re.sub(r'\s+', '', block)
    return block


def parse_css_file(filepath):
    """
    Parse the CSS file, yielding (context, selector, block_lines, start_line, end_line).
    Context is a tuple: (at_rule_type, at_rule_value) or ('root', None)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    context_stack = [('root', None)]  # Stack of (at_rule_type, at_rule_value)
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        # Detect at-rules (e.g., @media)
        at_rule_match = re.match(r'\s*@(media|supports|keyframes)[^{]*\{', line)
        if at_rule_match:
            # Enter new context
            at_rule_type = at_rule_match.group(1)
            at_rule_value = line.strip()
            context_stack.append((at_rule_type, at_rule_value))
            i += 1
            continue
        # Detect end of context
        if line.strip() == '}':
            if len(context_stack) > 1:
                context_stack.pop()
            i += 1
            continue
        # Detect class selector at current context
        selector_match = re.match(r'\s*([.#][\w\-][^{]*)\s*\{', line)
        if selector_match:
            selector = selector_match.group(1).strip()
            block_lines = [line]
            start_line = i
            brace_count = line.count('{') - line.count('}')
            i += 1
            # Read until block closes
            while i < n and brace_count > 0:
                block_lines.append(lines[i])
                brace_count += lines[i].count('{') - lines[i].count('}')
                i += 1
            end_line = i - 1
            yield (tuple(context_stack), selector, block_lines, start_line, end_line)
            continue
        i += 1


def dedupe_css(filepath, output_path):
    """
    Remove duplicate class definitions within the same context.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Map: context -> selector -> list of (norm_block, start, end, block_lines)
    registry = defaultdict(lambda: defaultdict(list))
    # Mark lines to remove
    remove_lines = set()

    for context, selector, block_lines, start, end in parse_css_file(filepath):
        norm_block = normalize_css_block(block_lines)
        found_duplicate = False
        for prev_norm, prev_start, prev_end, _ in registry[context][selector]:
            if norm_block == prev_norm:
                # Duplicate found, mark for removal
                remove_lines.update(range(start, end + 1))
                found_duplicate = True
                break
        if not found_duplicate:
            registry[context][selector].append((norm_block, start, end, block_lines))

    # Write output, skipping removed lines
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, line in enumerate(lines):
            if idx not in remove_lines:
                f.write(line)

if __name__ == '__main__':
    dedupe_css(CSS_FILE, OUTPUT_FILE) 