"""
Demo: Get all nodes of a model and print their coordinates.
Requires META to be running with a model loaded.
"""
import meta
from meta import nodes, models, utils


def main():
    # Get all loaded models
    all_models = utils.get_models()
    if not all_models:
        print("No models loaded.")
        return

    mdl = all_models[0]
    print(f"Model: {mdl.id} — {mdl.name}")

    # Collect all nodes
    all_nodes = nodes.get_nodes(mdl.id)
    print(f"Total nodes: {len(all_nodes)}")

    # Print first 10
    for nd in all_nodes[:10]:
        print(f"  Node {nd.id}: x={nd.x:.3f}  y={nd.y:.3f}  z={nd.z:.3f}")


if __name__ == "__main__":
    main()
