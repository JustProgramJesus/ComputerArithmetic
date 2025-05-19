from django.shortcuts import render
from .utils import generate_logic_graph, OPERATIONS
import json

OP_SYMBOLS = {
    "OR": "∨", "AND": "∧", "XOR": "⊕", "EQUIV": "≡", "IMPLIES": "→",
    "NAND": "↑", "NOR": "↓", "NOT_IMPLIES": "↛", "NOT_X": "¬x", "X": "x",
    "Y": "y", "LEFT": "←", "NOT_LEFT": "↚", "NOT_Y": "¬y"
}

def graph_view(request):
    levels = generate_logic_graph()
    elements = []
    level_labels = []
    table_data = []

    for level_idx, level in enumerate(levels):
        level_y = level_idx * 200
        level_labels.append({"y": level_y, "top_adjusted": level_y + 30, "label": f"Уровень {level_idx}"})

        for node_idx, node in enumerate(level):
            node_id = f"Y{level_idx}_{node_idx}"
            x = node_idx * 200
            y = level_y

            if level_idx == 0:
                base, val_base, bin_val = node
                label = f"[{val_base}]"
                data_label = f"[{val_base}]"
                bin_label = f"[{bin_val}]₂"
                op = "INPUT"
                inputs = "-"
            else:
                op_code = node[0]
                inputs = node[1:-3]
                base = node[-3]
                val_base = node[-2]
                bin_val = node[-1]
                symbol = OP_SYMBOLS.get(OPERATIONS[op_code], OPERATIONS[op_code])
                label = symbol
                data_label = f"[{val_base}]₍{base}₎"
                bin_label = f"[{bin_val}]₂"
                for src in inputs:
                    elements.append({"data": {
                        "source": f"Y{level_idx - 1}_{src}", "target": node_id
                    }})

            elements.append({
                "data": {"id": node_id, "label": label, "dataLabel": data_label, "binLabel": bin_label},
                "position": {"x": x, "y": y}
            })

            table_data.append({
                "level": level_idx,
                "node": node_idx,
                "operation": label,
                "inputs": inputs if isinstance(inputs, str) else ", ".join(map(str, inputs)),
                "base": base,
                "result": val_base,
                "bin": bin_val
            })

    return render(request, "logic_app/graph.html", {
        "elements": json.dumps(elements),
        "level_labels": json.dumps(level_labels),
        "table_data": table_data,
    })