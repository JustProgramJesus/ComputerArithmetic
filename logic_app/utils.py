import random

# Конфигурация
MAX_LEVELS = 10
MAX_NODES_PER_LEVEL = 10
MAX_NUMBER = 10000
MAX_BASE = 16

OPERATIONS = [
    "OR", "AND", "XOR", "EQUIV", "IMPLIES", "NAND", "NOR",
    "NOT_IMPLIES", "NOT_X", "X", "Y", "LEFT", "NOT_LEFT", "NOT_Y"
]

OPERATION_INPUT_RULES = {
    0: (2, None), 1: (2, None), 2: (2, None), 3: (2, None),
    4: (2, 2), 5: (2, None), 6: (2, None), 7: (2, 2),
    8: (1, 1), 9: (1, 1), 10: (2, 2), 11: (2, 2),
    12: (2, 2), 13: (2, 2)
}


def int_to_base(n, base):
    digits = "0123456789ABCDEF"
    if n == 0:
        return "0"
    res = ""
    while n > 0:
        res = digits[n % base] + res
        n //= base
    return res


def apply_operation(op_code, inputs_bin):
    length = len(inputs_bin[0])
    result = []
    for i in range(length):
        try:
            bits = [int(x[i]) for x in inputs_bin]
        except IndexError:
            return '0' * length
        a = bits[0]
        b = bits[1] if len(bits) > 1 else 0

        match OPERATIONS[op_code]:
            case "AND": res = a & b
            case "OR": res = a | b
            case "XOR": res = a ^ b
            case "EQUIV": res = int(not (a ^ b))
            case "IMPLIES": res = int((not a) | b)
            case "NAND": res = int(not (a & b))
            case "NOR": res = int(not (a | b))
            case "NOT_IMPLIES": res = int(not ((not a) | b))
            case "NOT_X": res = int(not a)
            case "X": res = a
            case "Y": res = b
            case "LEFT": res = int((not b) | a)
            case "NOT_LEFT": res = int(not ((not b) | a))
            case "NOT_Y": res = int(not b)
            case _: res = 0
        result.append(str(res))
    return ''.join(result)


def generate_quasi_uniform_bases(count, min_base=2, max_base=10):
    bases = list(range(min_base, max_base + 1))
    result = []
    while len(result) < count:
        result.extend(bases)
    random.shuffle(result)
    return result[:count]


def generate_logic_graph():
    num_levels = random.randint(2, MAX_LEVELS)
    levels = []
    structure = tuple(random.randint(1, MAX_NODES_PER_LEVEL) for _ in range(num_levels))

    level0_count = structure[0]
    bases0 = generate_quasi_uniform_bases(level0_count, 2, MAX_BASE)
    current_level = []

    nums0 = list(range(0, MAX_NUMBER, max(1, MAX_NUMBER // level0_count)))
    while len(nums0) < level0_count:
        nums0.append(random.randint(0, MAX_NUMBER))
    random.shuffle(nums0)
    nums0 = nums0[:level0_count]

    for base, num in zip(bases0, nums0):
        val_in_base = int_to_base(num, base)
        val_in_bin = bin(num)[2:].zfill(16)
        current_level.append([base, val_in_base, val_in_bin])
    levels.append(current_level)

    for level_index in range(1, num_levels):
        level_node_count = structure[level_index]
        current_level = []
        prev_level = levels[level_index - 1]
        available_inputs = len(prev_level)

        for _ in range(level_node_count):
            valid_ops = [op for op in range(len(OPERATIONS)) if OPERATION_INPUT_RULES[op][0] <= available_inputs]
            if not valid_ops:
                op_code = 9
                min_inputs_rule, max_inputs_rule = 1, 1
            else:
                op_code = random.choice(valid_ops)
                min_inputs_rule, max_inputs_rule = OPERATION_INPUT_RULES[op_code]
            max_possible = available_inputs if max_inputs_rule is None else min(max_inputs_rule, available_inputs)
            input_count = random.randint(min_inputs_rule, max_possible)
            inputs = sorted(random.sample(range(available_inputs), input_count))
            node = [op_code] + inputs
            current_level.append(node)
        levels.append(current_level)

    for level_index in range(1, num_levels):
        prev_level = levels[level_index - 1]
        current_level = levels[level_index]
        out_bases = generate_quasi_uniform_bases(len(current_level), 2, MAX_BASE)

        for idx, operation in enumerate(current_level):
            op_code = operation[0]
            input_indices = operation[1:]
            inputs_bin = []
            for i in input_indices:
                if 0 <= i < len(prev_level):
                    node_bin = prev_level[i][-1]
                    if isinstance(node_bin, str):
                        inputs_bin.append(node_bin)
            result_bin = apply_operation(op_code, inputs_bin) if inputs_bin else '0' * 16
            res_int = int(result_bin, 2)
            out_base = out_bases[idx]
            result_in_base = int_to_base(res_int, out_base)
            operation.extend([out_base, result_in_base, result_bin])

    return tuple(levels)