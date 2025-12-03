from fastapi import FastAPI, Query
import subprocess

app = FastAPI()

@app.get("/generate")
def generate(
    filter: str = Query(""),
    difficulty: str = Query("easy"),
    count: int = Query(1),
    entropy_range: str = Query(None),
):
    cmd = [
        "python",
        "-m",
        "mathematics_dataset.custom_generate_by_difficulty",
        f"--filter={filter}",
        f"--count={count}",
        f"--difficulty={difficulty}"
    ]

    if entropy_range:
        cmd.append(f"--entropy_range={entropy_range}")

    # Capture CLI output
    result = subprocess.check_output(cmd).decode().strip().split("\n")

    # Convert Q/A into structured JSON
    items = []
    for i in range(0, len(result), 2):
        q = result[i]
        a = result[i + 1] if i + 1 < len(result) else ""
        items.append({"question": q, "answer": a})

    return {"items": items}
