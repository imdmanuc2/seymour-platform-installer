from pathlib import Path
import sys

repo = Path(sys.argv[1])
path = repo / "lib/state/store.py"
text = path.read_text()

if "from lifecycle.transaction import initialize_transaction" not in text:
    text = text.replace(
        "from lifecycle.operation import initialize_operation_record\n",
        "from lifecycle.operation import initialize_operation_record\n"
        "from lifecycle.transaction import initialize_transaction\n",
    )

text = text.replace(
    "        initialize_operation_record(operation)\n"
    "        self.save_operation(operation)\n",
    "        initialize_operation_record(operation)\n"
    "        initialize_transaction(operation)\n"
    "        self.save_operation(operation)\n",
)

text = text.replace(
    "        return initialize_operation_record(\n"
    "            json.loads(path.read_text())\n"
    "        )\n",
    "        operation = initialize_operation_record(\n"
    "            json.loads(path.read_text())\n"
    "        )\n"
    "        initialize_transaction(operation)\n"
    "        return operation\n",
)

path.write_text(text)
