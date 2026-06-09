"""
Demo: Create a fringe plot of von Mises stress for the first model.
Requires META to be running with results loaded.
"""
import meta
from meta import results, models, utils, visuals


def main():
    # Get all loaded models
    all_models = utils.get_models()
    if not all_models:
        print("No models loaded.")
        return

    mdl = all_models[0]
    print(f"Model: {mdl.id} — {mdl.name}")

    # List available result cases
    cases = results.get_result_cases(mdl.id)
    print(f"Result cases: {len(cases)}")
    for c in cases[:5]:
        print(f"  Case {c.id}: {c.name}")


if __name__ == "__main__":
    main()
