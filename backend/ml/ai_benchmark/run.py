import asyncio
import json
import time
from pathlib import Path

from app.ai.orchestrator import orchestrator
from app.ai.critical_symptoms import detect_critical_symptoms


DATASET = Path("ml/ai_benchmark/cases.json")
CASE_TIMEOUT = 30


async def run_case(text):
    try:
        return await asyncio.wait_for(
            orchestrator.extract(text),
            timeout=CASE_TIMEOUT
        )
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "validated": False,
            "result": {
                "symptoms": []
            },
            "error": f"case exceeded {CASE_TIMEOUT}s timeout"
        }
    except Exception as exc:
        return {
            "status": "failed",
            "validated": False,
            "result": {
                "symptoms": []
            },
            "error": str(exc)
        }


async def main():

    cases = json.loads(
        DATASET.read_text(encoding="utf-8")
    )

    tp = 0
    fp = 0
    fn = 0

    results = []

    for index, case in enumerate(cases, 1):

        start = time.perf_counter()

        ai_response = await run_case(case["text"])

        safety = detect_critical_symptoms(case["text"])

        predicted = set()

        if (
            ai_response.get("status") == "success"
            and ai_response.get("result")
        ):
            predicted = {
                item["name"]
                for item in ai_response["result"].get("symptoms", [])
            }

        for item in safety:
            predicted.add(item["symptom"])

        expected = set(case["expected"])

        case_tp = len(predicted & expected)
        case_fp = len(predicted - expected)
        case_fn = len(expected - predicted)

        tp += case_tp
        fp += case_fp
        fn += case_fn

        elapsed = time.perf_counter() - start

        results.append({
            "case": index,
            "text": case["text"],
            "expected": sorted(expected),
            "predicted": sorted(predicted),
            "true_positive": case_tp,
            "false_positive": case_fp,
            "false_negative": case_fn,
            "safety_matches": safety,
            "status": ai_response.get("status"),
            "error": ai_response.get("error"),
            "latency_seconds": round(elapsed, 3)
        })

        print(
            f"[{index}/{len(cases)}] "
            f"TP={case_tp} "
            f"FP={case_fp} "
            f"FN={case_fn} "
            f"{elapsed:.2f}s "
            f"STATUS={ai_response.get('status')}"
        )

    precision = (
        tp / (tp + fp)
        if tp + fp
        else 0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0
    )

    latencies = [
        r["latency_seconds"]
        for r in results
    ]

    timed_out = [
        r for r in results
        if r["status"] == "timeout"
    ]

    report = {
        "cases": len(cases),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "timeout_seconds": CASE_TIMEOUT,
        "timed_out_cases": len(timed_out),
        "latency": {
            "min": round(min(latencies), 3),
            "max": round(max(latencies), 3),
            "average": round(
                sum(latencies) / len(latencies),
                3
            )
        },
        "results": results
    }

    output = Path("ml/ai_benchmark/report.json")

    output.write_text(
        json.dumps(
            report,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print("=== AEGIS AI BENCHMARK ===")
    print(f"Precision: {precision:.2%}")
    print(f"Recall:    {recall:.2%}")
    print(f"F1:        {f1:.2%}")
    print(f"Timeouts:  {len(timed_out)}")
    print(f"Min:       {min(latencies):.2f}s")
    print(f"Max:       {max(latencies):.2f}s")
    print(
        f"Average:   "
        f"{sum(latencies) / len(latencies):.2f}s"
    )
    print(f"Report:    {output}")


if __name__ == "__main__":
    asyncio.run(main())
