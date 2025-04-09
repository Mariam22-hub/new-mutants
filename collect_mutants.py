
import os
import json
import sys
import pickle

project_names = [
    "commons-csv", "commons-cli", "commons-collections", "commons-compress", "commons-codec", 
    "gson", "jsoup", "commons-lang", "commons-jxpath", "jfreechart", "joda-time", "jackson-dataformat-xml", "jackson-databind",
    "jackson-core", "commons-math"
]

def collect_mutants(technique: str, projects: list, output_dir: str) -> dict:
    """Collects all unused mutants for each project and stores them in a map."""
    project_to_mutants = {}

    for project in projects:
        file_path = os.path.join(output_dir, technique, f'{project}.jsonl')

        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r') as f:
            lines = f.readlines()

        project_to_mutants[project] = []
        for idx, line in enumerate(lines):
            full_entry = json.loads(line)
            unused_mutants = list(full_entry["final"])

            # print(method["index"] + " in project " + project)
            for mutant in unused_mutants:
                project_to_mutants[project].append({
                    "full_entry": full_entry,
                    "mutant": mutant,
                    "line_idx": idx
                })
                print(len(project_to_mutants[project]))

    return project_to_mutants

def save_mutants_to_file(project_to_mutants: dict, technique: str):
    """Saves the collected mutants to a JSON file for later use."""
    os.makedirs("mutants_pk", exist_ok=True)
    with open(f'mutants_pk/{technique}_mutants.pk', 'wb') as f:
        pickle.dump(project_to_mutants, f)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <technique> <output_dir>")
        exit(1)

    techniques = sys.argv[1].split(',')
    output_dir = sys.argv[2]

    for technique in techniques:
        print(f"Fetching the unused mutants for {technique.strip()}")
        project_to_mutants = collect_mutants(technique.strip(), project_names, output_dir)
        
        print(f"Saving collected mutants for {technique.strip()}")
        save_mutants_to_file(project_to_mutants, technique.strip())
        print(f"Finished saving mutants to {technique.strip()}_mutants.pk")
