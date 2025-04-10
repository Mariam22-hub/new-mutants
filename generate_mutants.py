import os
import json
import re
import random
from tqdm.auto import tqdm
from pathlib import Path
import sys
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Lock, Manager
import pickle
# from format_mutants import format_java_code

project_names = [
    "commons-csv", "commons-cli", "commons-collections", "commons-compress", "commons-codec", 
    "jsoup", "commons-lang", "commons-jxpath", "jfreechart", "joda-time", "jackson-dataformat-xml", "jackson-databind",
    "jackson-core", "commons-math", "gson"
]

def git_operations(file_path: str, project: str, technique: str, method_idx: int, line_idx: int, 
                   buggy_method_number: int, projects_path: str):
    
    """Handles the Git operations: creating a branch, committing the change, and pushing the branch."""
    
    # Generate the branch name based on the provided convention
    branch_name = f"{technique}-base.{project}.mid-{method_idx}.idx-{line_idx}.{buggy_method_number}.mutant"
    
    # Initialize git repository and create a new branch
    original_directory = os.getcwd()
    os.chdir(projects_path)
    
    project_index = file_path.find(project)
    if project_index != -1:
        file_path = file_path[project_index:] 

    result = subprocess.run(['git', 'checkout', '-b', branch_name])
    print("Executing: ", result.args)
    if result.returncode != 0:
        exit(1)

    # Add, commit, and push changes
    format_result = subprocess.run(['google-java-format', '-i', file_path])
    print("Executing: ", result.args)
    if format_result.returncode != 0:
        print(f"Failed to format the file: {file_path}")
        subprocess.run(['git', 'checkout', "main"])
        return False

    result = subprocess.run(['git', 'add', file_path])
    print("Executing: ", result.args)
    if result.returncode != 0:
        exit(1)
    commit_message = f"{branch_name}"
    result = subprocess.run(['git', 'commit', '-m', commit_message])
    print("Executing: ", result.args)
    if result.returncode != 0:
        exit(1)

    # Create a formatted-main branch for diff with formatted main java code
    result = subprocess.run(['git', 'checkout', "main"])
    print("Executing: ", result.args)
    if result.returncode != 0:
        exit(1)
    result = subprocess.run(['git', 'checkout', '-b', f'formatted-main-{branch_name}'])
    print("Executing: ", result.args)
    if result.returncode != 0:
        exit(1)
    result = subprocess.run(['google-java-format', '-i', file_path])
    print("Executing: ", result.args)
    if result.returncode != 0:
        exit(1)
    result = subprocess.run(['git', 'add', file_path])
    print("Executing: ", result.args)
    if result.returncode != 0:
        exit(1)
    result = subprocess.run(['git', 'commit', '-m', f"Formatted main branch before {branch_name} injection"])
    print("Executing: ", result.args)
    if result.returncode != 0:
        exit(1)
    # result = subprocess.run(['git', 'push', 'origin', f'formatted-main-{branch_name}'])
#     print("Executing: ", result.args)
    # if result.returncode != 0:
    #     exit(1)

    # # Push the branch to remote repository
    # push_result = result = subprocess.run(['git', 'push', 'origin', branch_name], capture_output=True, text=True)
#     print("Executing: ", result.args)
    # if result.returncode != 0:
    #     exit(1)

    result = subprocess.run(['git', 'checkout', "main"])
    print("Executing: ", result.args)
    if result.returncode != 0:
        exit(1)
    # if push_result.returncode == 0:
    #     print(f"Branch '{branch_name}' pushed successfully!")
    #     print(f"Switching back to main")
    #     # git diff formatted-main mutant-branch
    # Print diff with colors
    subprocess.run(['git', '--no-pager', 'diff', f'formatted-main-{branch_name}', branch_name])

    result = subprocess.run(['git', '--no-pager', 'diff', f'formatted-main-{branch_name}', branch_name], capture_output=True, text=True)
    if result.stdout == '':
        print(f"No difference found between formatted main and {branch_name} branch.")
        with open('../empty_diff.txt', 'a') as f:
            f.write(f"{branch_name}\n")
    else:
        # Check if stdout is more than 50 lines
        stdout_lines = result.stdout.count('\n')
        if stdout_lines > 50:
            print(f"Diff is too long ({stdout_lines} lines), saving to too_long.txt")
            with open('../too_long.txt', 'a') as f:
                f.write(f"{branch_name}: {stdout_lines} lines\n")
    # if result.returncode != 0:
    #     exit(1)
    #     result = subprocess.run(['git', 'checkout', "main"])
#     print("Executing: ", result.args)
    # if result.returncode != 0:
    #     exit(1)
    os.chdir(original_directory)
    return True
    #     return True
    # else:
    #     print(f"Failed to push branch '{branch_name}'. Error: {push_result.stderr}")
    #     return False

def inject_mutant_and_commit(file_path: str, start: int, end: int, code: str, project: str, 
                             technique: str, method_idx: int, line_idx: int, buggy_method_number: int, 
                             projects_path: str) -> bool:
    
    """Injects a mutant into the code and tests if it is compilable"""
    file_path = file_path.replace("projects", projects_path)
    print(f"Injecting mutant into: {file_path}")
    
    os.makedirs('generated_mutants', exist_ok=True)

    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    start = int(start)
    end = int(end)
    
    original_code = ''.join(lines[start - 1: end])
    if original_code == code:
        return False
  
    # Injecting
    new_lines = ''.join(lines[:start - 1]) + code + ''.join(lines[end:])
    with open(file_path, 'w') as f:
        # # Format Java code before writing
        # formatted_code = format_java_code(new_lines)
        # if formatted_code == "":
        #     return False
        f.write(new_lines)

    status = git_operations(file_path, project, technique, method_idx, line_idx, 
                            buggy_method_number, projects_path)

    # compiling
    # script_directory = os.getcwd()
    # os.chdir(os.path.join(projects_path, project))
    # is_compilable = os.system('timeout 180 mvn -q compile -Dfile={file_path}')
    # print("Is compilable? ", is_compilable)
    # os.chdir(script_directory)

    # Reverting the change
    with open(file_path, 'w') as f:
        f.writelines(lines)

    # if is_compilable != 0:
    #     return False
        
    return status


def process_single_mutant(selected, technique, projects_path, lock):
    """Compile a single mutant and return the result."""
    full_entry = selected['full_entry']
    sampled = selected['mutant']
    line_idx = selected['line_idx']
    field_name = f'buggy_method{sampled}'

    # status = inject_mutant_and_compile(full_entry['file_path'], full_entry['start_line'], full_entry['end_line'], full_entry[field_name], full_entry['project'], projects_path)
    status = inject_mutant_and_commit(
        full_entry['file_path'], 
        full_entry['start_line'], 
        full_entry['end_line'], 
        full_entry[field_name], 
        full_entry['project'], 
        technique, 
        full_entry['index'], 
        line_idx+1, 
        sampled, 
        projects_path
    )

    result = {
        "status": status,
        "project": full_entry['project'],
        # "method": full_entry,
        # "sampled": sampled,
        # "line_idx": line_idx,
        # "technique": technique
    }

    # Write result to file with lock
    if status:
        reproduced_mutant = {
            "line_idx": line_idx+1,
            "func": full_entry['method'],
            "target": 1,
            "method_idx": full_entry['index'],
            "project": full_entry['project'],
            "file_path": full_entry["file_path"],
            f"buggy_method{sampled}": full_entry[field_name],
            "start_line": full_entry["start_line"],
            "end_line": full_entry["end_line"]
        }
        
        # print("Mutant " +  field_name + " for project " + full_entry["project"] + " compiled")
        
        with lock:
            with open(f'generated_mutants/{technique}_compilable_mutants.jsonl', 'a') as output_file:
                output_file.write(json.dumps(reproduced_mutant) + '\n')

    return result

def random_selection(project_to_mutants: dict, desired_count: int, technique: str, projects: list, projects_path: str):
    """Randomly selects and compiles mutants until the desired count is reached."""
    count = 0
    found = 0

    # total_tests_tried = 0
    # overall_failed_tests = 0
    # project_failed_tests = {project: 0 for project in projects}
    project_mutants_chosen = {project: 0 for project in projects}

    # Using Manager to create a shared lock
    with Manager() as manager:
        lock = manager.Lock()

        with tqdm(total=desired_count, desc=f"Processing Mutants for {technique}") as pbar:
            with ProcessPoolExecutor(max_workers=1) as executor:
                
                while found < desired_count:
                    count += 1
                    project = random.choice(projects)

                    if project not in project_to_mutants or not project_to_mutants[project]:
                        continue

                    # Randomly select a mutant
                    selected = random.choice(project_to_mutants[project])

                    # Submit the task and get the future
                    future = executor.submit(process_single_mutant, selected, technique, projects_path, lock)

                    # Process the result immediately after the task is completed
                    result = future.result()
                    # total_tests_tried += 1
                    project_mutants_chosen[result["project"]] += 1

                    if result["status"]:
                        found += 1
                        pbar.update(1)  # Update progress bar on successful mutants
                    # else:
                        # project_failed_tests[result["project"]] += 1
                        # overall_failed_tests += 1

                    # Remove the tested mutant from the map
                    project_to_mutants[result["project"]].remove(selected)

    for project in projects:
        print(f"{project} - Mutants Chosen: {project_mutants_chosen[project]}")


def load_mutants_from_pk_file(technique: str) -> dict:
    """Loads previously collected mutants from a PK file."""
    file_path = f'mutants_pk/{technique}_mutants.pk'
    if not os.path.exists(file_path):
        print(f"No saved mutants found for {technique}, please run the collection script first.")
        exit(1)

    with open(file_path, 'rb') as f:
        return pickle.load(f)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <techniques> <desired_mutants_count> <projects_directory")
        print("<techniques> should be a comma-separated list like 'leam'")
        # print("<output_dir> is the directory where outputs will be read from and saved to")
        print("<desired_mutants_count> is the number of mutants to reproduce")
        print("<projects_directory> is where the java projects are contained")
        exit(1)

    techniques = sys.argv[1].split(',')
    # output_dir = sys.argv[2]
    desired_mutants_count = int(sys.argv[2])
    projects_path = sys.argv[3]

    random.seed()
    
    for technique in techniques:
        if os.path.exists(f"{technique}_compilable_tested_mutants.jsonl"):
            os.remove(f"{technique}_compilable_tested_mutants.jsonl")
        
        print(f"Fetching the unused mutants for {technique}")
        project_to_mutants = load_mutants_from_pk_file(technique)
        print(f"Finished fetching the unused mutants for {technique}")
        print(f"Starting generating mutants for {technique}")
        random_selection(project_to_mutants, desired_mutants_count, technique, project_names, projects_path)
        print("Finished selecting mutants!")




# def collect_mutants(technique: str, projects: list, output_dir: str) -> dict:
    # """Collects all unused mutants for each project, and store then in a map."""
    # project_to_mutants = {}
    # for project in projects:
    #     file_path = os.path.join(output_dir, technique, f'{project}.jsonl')
        
    #     if not os.path.exists(file_path):
    #         continue
        
    #     with open(file_path, 'r') as f:
    #         lines = f.readlines()

    #     project_to_mutants[project] = []
    #     for idx, line in enumerate(lines):
    #         method = json.loads(line)
    #         unused_mutants = list(method["final"])
    #         # print(unused_mutants)
    #         print(method["index"] + " in project " + project)
    #         for mutant in unused_mutants:
    #             project_to_mutants[project].append({
    #                 "method": method,
    #                 "mutant": mutant,
    #                 "line_idx": idx
    #             })
    #             print(len(project_to_mutants[project]))

    # return project_to_mutants


# import os
# import json
# import re
# import random
# from tqdm.auto import tqdm
# from pathlib import Path
# import sys
# import subprocess

# project_names = [
#     "commons-csv", "commons-cli", "commons-collections", "commons-compress", "commons-codec", 
#     "gson", "jsoup", "commons-lang", "commons-jxpath", "jfreechart", "joda-time", "jackson-dataformat-xml", "jackson-databind",
#     "jackson-core", "commons-math"
# ]


# def inject_mutant_and_test(file_path: str, start: int, end: int, code: str, project: str, projects_path: str) -> bool:
#     """Injects a mutant into the code and tests if it is compilable and passes all tests."""
#     file_path = file_path.replace("projects", projects_path)
#     with open(file_path, 'r') as f:
#         lines = f.readlines()

#     original_code = ''.join(lines[start - 1: end])
#     if original_code == code:
#         return False
  
#     # Injecting
#     new_lines = ''.join(lines[:start - 1]) + code + ''.join(lines[end:])
#     with open(file_path, 'w') as f:
#         f.write(new_lines)

#     script_directory = os.getcwd()
#     os.chdir(os.path.join(projects_path, project))
#     is_compilable = os.system('timeout 60 mvn test > ../../tmp.log')
#     os.chdir(script_directory)

#     # Reverting the change
#     with open(file_path, 'w') as f:
#         f.writelines(lines)

#     if is_compilable != 0:
#         return False

#     # Checking if all tests passed
#     with open('tmp.log', 'r') as f:
#         lines = f.readlines()
#         test_result_line = list(filter(lambda x: "Tests run" in x, lines))[-1]
#         temp = re.findall(r'\d+', test_result_line)[-4:]  # Numbers in the front are color information
#         test_result = list(map(int, temp))  # [total tests run, failures, errors, skipped]
        
#         if test_result[1] != 0 or test_result[2] != 0:
#             return False
        
#     return True

# def collect_mutants(technique: str, projects: list, output_dir: str) -> dict:
#     """Collects all unused mutants for each project, and store then in a map."""
#     project_to_mutants = {}
#     for project in projects:
#         file_path = os.path.join(output_dir, technique, f'{project}.jsonl')
        
#         if not os.path.exists(file_path):
#             continue
        
#         with open(file_path, 'r') as f:
#             lines = f.readlines()

#         project_to_mutants[project] = []
#         for idx, line in enumerate(lines):
#             method = json.loads(line)
#             unused_mutants = list(set(method['selected_bugs']) - set(method['confirmed_bugs']) - set(method['uiucplus_mutant']))
            
#             for mutant in unused_mutants:
#                 project_to_mutants[project].append({
#                     "method": method,
#                     "mutant": mutant,
#                     "line_idx": idx
#                 })

#     return project_to_mutants

# def random_selection(project_to_mutants: dict, desired_count: int, technique: str, projects: list, projects_path: str):
#     """Randomly selects and tests mutants until the desired count is reached."""
#     # reproduced_mutants = []
#     count = 0
#     found = 0

#     total_tests_tried = 0
#     overall_failed_tests = 0
#     project_failed_tests = {project: 0 for project in projects}
#     project_mutants_chosen = {project: 0 for project in projects}

#     with tqdm(total=desired_count, desc=f"Testing Mutants for {technique}") as pbar:
#         while found < desired_count:
#             count += 1
#             project = random.choice(projects)
#             if project not in project_to_mutants or not project_to_mutants[project]:
#                 continue
            
#             selected = random.choice(project_to_mutants[project])
#             method = selected['method']
#             sampled = selected['mutant']
#             line_idx = selected['line_idx']
#             field_name = f'buggy_method{sampled}'

#             print(f'{count}\t{found}\t project: {project}, line_idx: {line_idx}, buggy_method{sampled}')
#             status = inject_mutant_and_test(method['file_path'], method['start_line'], method['end_line'], method[field_name], method['project'], projects_path)
#             print(f'\t\tstatus: {status}')

#             total_tests_tried += 1
#             project_mutants_chosen[project] += 1

#             if status:
#                 reproduced_mutant = {
#                     "line_idx": found,
#                     "func": method['method'],
#                     "target": 1,
#                     "method_idx": method['index'],
#                     "project": method['project'],
#                     f"buggy_method{sampled}": method[field_name],
#                     "start_line": method["start_line"],
#                     "end_line": method["end_line"]
#                 }
#                 found += 1
#                 pbar.update(1)

#                 with open(f'{technique}_compilable_tested_mutants.jsonl', 'a') as output_file:
#                     output_file.write(json.dumps(reproduced_mutant) + '\n')
#             else:
#                 project_failed_tests[project] += 1
#                 overall_failed_tests += 1

#             # Remove the tested mutant from the map
#             project_to_mutants[project].remove(selected)

#     # Logging summary
#     print("\nSummary of Mutant Testing:")
#     print(f"Total Tests Tried: {total_tests_tried}")
#     print(f"Overall Failed Tests: {overall_failed_tests}")
#     for project in projects:
#         print(f"{project} - Mutants Chosen: {project_mutants_chosen[project]}, Failed Tests: {project_failed_tests[project]}")

# if __name__ == '__main__':
#     if len(sys.argv) != 5:
#         print(f"Usage: {sys.argv[0]} <techniques> <output_dir> <desired_mutants_count>")
#         print("<techniques> should be a comma-separated list like 'leam'")
#         print("<output_dir> is the directory where outputs will be read from and saved to")
#         print("<desired_mutants_count> is the number of mutants to reproduce")
#         print("<projects_directory> is where the java projects are contained")
#         exit(1)

#     techniques = sys.argv[1].split(',')
#     output_dir = sys.argv[2]
#     desired_mutants_count = int(sys.argv[3])
#     projects = sys.argv[4]

#     print("checking the required tools")
#     random.seed(27)
    
#     for technique in techniques:
#         if os.path.exists(f"{technique}_compilable_tested_mutants.jsonl"):
#             os.remove(f"{technique}_compilable_tested_mutants.jsonl")
        
#         print(f"Fetching the unused mutants for {technique}")
#         project_to_mutants = collect_mutants(technique, project_names, output_dir)
#         print(f"Finished fetching the unused mutants for {technique}")
#         random_selection(project_to_mutants, desired_mutants_count, technique, project_names, projects)
#         print("Finished selecting mutants!")
