# Import necessary libraries
import pandas as pd
import sys
import time
import json
import os
from tqdm.auto import tqdm  # For progress bar

# List of Java projects to process
project_names = [
    "commons-csv", "commons-cli", "commons-collections", "commons-compress", "commons-codec", 
    "gson", "jsoup", "commons-lang", "commons-jxpath", "jfreechart", "joda-time", 
    "jackson-dataformat-xml", "jackson-databind", "jackson-core", "commons-math"
]

# Counter for total number of compilable mutants (not being used currently, just printed at the end)
count = 0

# Load the CSV file that contains info about mutants that successfully compile
combined_mutants = pd.read_csv("combined_techniques_projects.csv")

# This function processes one project + technique at a time
def process_project_technique(project_name, technique, data_dir, defect_dir, output_dir, uiuc_mutant):

    # Identify the correct path to the "unconfirmed bugs" file depending on the technique
    if technique in ['mubert', 'leam']:
        unconfirmed_bug_file = os.path.join(data_dir, technique, f'{project_name}.jsonl')
    elif technique in ['codebert', 'codet5', 'NatGen']:
        unconfirmed_bug_file = os.path.join(data_dir, project_name, f'unique_methods_{technique}-base_selected_bugs.jsonl')
    else:
        print(f"Technique {technique} is not supported.")
        return  # Exit if unsupported technique

    # Path to the confirmed bugs file (common format for all techniques)
    confirmed_bug_file = os.path.join(defect_dir, f'{technique}-base_all_confirmed_bugs_method_id.jsonl')

    # Make sure the output directories exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    technique_dir = os.path.join(output_dir, technique)
    if not os.path.exists(technique_dir):
        os.makedirs(technique_dir)

    # Open output log and JSONL files
    log_file = open(os.path.join(output_dir, f'{project_name}_{technique}.csv'), 'w')
    output_file = open(os.path.join(technique_dir, f'{project_name}.jsonl'), 'w')

    # Write header to CSV log file
    log_file.write(f'method_idx,buggy_method,line_no\n')

    # Load unconfirmed bugs list (each line = one method's unconfirmed mutants)
    print(f"Reading UB file for {project_name} with technique {technique}")
    with open(unconfirmed_bug_file, 'r') as f:
        unconfirmed_bug = f.readlines()

    # Load confirmed bugs (structured as JSON lines)
    print(f"Reading CB file for {project_name} with technique {technique}")
    all_confirmed_bugs = pd.read_json(confirmed_bug_file, lines=True)

    # Iterate through each method entry in unconfirmed bugs
    for target_json in tqdm(unconfirmed_bug):
        target = json.loads(target_json)  # Parse one JSON object
        ks = target['selected_bugs']     # List of mutant indices for this method
        method_idx = target['index']     # Method index

        print("method_idx: ", method_idx)
        print("techqnique: ", technique)
        print("project: ", project_name)

        # Get confirmed bugs for this method and project
        confirmed_bug_dict = dict(
            all_confirmed_bugs[
                (all_confirmed_bugs['method_idx'] == method_idx) & 
                (all_confirmed_bugs['project'] == project_name)
            ]['func']
        )

        confirmed_bug_idx = []  # List to collect confirmed mutant indices

        # Loop through each mutant in selected_bugs
        for k in ks:
            buggy_method = target.get(f'buggy_method{k}')
            if buggy_method in confirmed_bug_dict.values():
                # Match found — log and keep the index
                bug = next(key for key, value in confirmed_bug_dict.items() if value == buggy_method)
                confirmed_bug_idx.append(k)
                log_file.write(f'{method_idx},{k},{bug}\n')

        target['confirmed_bugs'] = confirmed_bug_idx

        # Filter UIUCPlus mutants for this method
        mask = (
            (uiuc_mutant['technique'] == technique) & 
            (uiuc_mutant['method_idx'] == method_idx) & 
            (uiuc_mutant['project_name'] == project_name)
        )

        target['uiucplus_mutant'] = list(uiuc_mutant[mask].buggy_method_idx)

        # Now find the remaining mutants: not confirmed & not in UIUC
        temp = list(set(target['selected_bugs']) - set(target['confirmed_bugs']) - set(target['uiucplus_mutant']))

        macthed_mutants_jsonl = []

        # Check which remaining mutants are matched by filename
        for index in temp:
            filename = f"{project_name}.{method_idx}.{index}.{technique}-base.build.log"
            macthed_dict = combined_mutants.loc[combined_mutants["Filename"] == filename]
            if not macthed_dict.empty:
                macthed_mutants_jsonl.append(index)

        # Final candidates: remaining ∩ matched
        target["final"] = list(set(temp) & set(macthed_mutants_jsonl))

        # Write this processed method entry back to output
        output_file.write(json.dumps(target) + '\n')

    # Close files after finishing
    log_file.close()
    output_file.close()

# Main entry point of the script
if __name__ == "__main__":

    # Require exactly 5 arguments
    if len(sys.argv) != 6:
        print(f"Usage: {sys.argv[0]} <techniques> <data_dir> <defect_dir> <output_dir> <uiucplusMutant.csv>")
        print("<techniques> can be 'mubert,leam,codebert,codet5,NatGen'")
        print("<data_dir> is the directory containing input data")
        print("<defect_dir> is the directory containing defect data")
        print("<output_dir> is the directory where outputs will be saved")
        print("<uiucplusMutants.csv> where the 1500 mutants information is contained")
        exit(1)

    # Parse arguments
    techniques = sys.argv[1].split(',')  # List of techniques to process
    data_dir = sys.argv[2]
    defect_dir = sys.argv[3]
    output_dir = sys.argv[4]
    mutants_csv = sys.argv[5]

    # Load UIUCPlus mutants data
    uiuc_mutant = pd.read_csv(mutants_csv)

    # Make sure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Track execution time
    start = time.time()

    # Loop through all projects and techniques and process them
    for project_name in project_names:
        for technique in techniques:
            process_project_technique(project_name, technique.strip(), data_dir, defect_dir, output_dir, uiuc_mutant)

    end = time.time()

    # Print final stats
    print("compilable_mutants: ", count)  # (Currently unused, placeholder)
    print("Time Taken: ", end-start)
