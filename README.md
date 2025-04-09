# How to Run the Script

## Prerequisites

### 1. GitHub SSH Key Authentication
If you haven’t set up SSH keys for GitHub, follow the steps below:

1. **Generate a new SSH key pair** (if you haven't already):
   - Run `ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`.
   - Press `Enter` to accept the default location and choose a passphrase if desired.

2. **Add the generated public key** (`~/.ssh/id_rsa.pub`) to your GitHub account:
   - Go to GitHub > Settings > SSH and GPG Keys > New SSH Key.
   - Paste the content of `~/.ssh/id_rsa.pub` into the "Key" field and give it a title.

3. **Ensure the SSH agent is running** and that your key is added:
   - Run the following commands:
     ```bash
     eval "$(ssh-agent -s)"
     ssh-add ~/.ssh/id_rsa
     ```

4. **Verify SSH authentication** by running:
   ```bash
   ssh -T git@github.com
### 2. Install tqdm
 ```bash
     pip install tqdm
 ```
# How to Run the Script

1. **Clone the Repository**
    
    * First, ensure that the repository is cloned to your local machine and that you have access to the GitHub repository via SSH.
          
        ```bash
        git clone git@github.com:<username>/<repository-name>.git
        ```

2. **Navigate to the Script Directory**
    
    * Change into the directory where the scripts are located:
        
        ```bash
        cd path/to/script
        ```

3. **Run the Script**
   1. First run the ```checkMatch.py``` script to generate the outputs directory containing all the mutants which are: ```unconfirmed - confirmed - uiucplus```
     
    * Use the following command format to run the script:
        
        ```bash
        python checkMatch.py <techniques> <data_dir> <defect_dir> <output_dir> <uiucplusMutant.csv>
        ```
      * **Example:**
        
        ```bash
        pythoncheckMatch.py path/to/data path/to/defect path/to/output leam path/to/uiucplusMutant.csv
        ```
   2. Second run the ```collect_mutants.py``` script to convert the mutants from jsonl to pk files for faster retrieval
     
    * Use the following command format to run the script:
        
        ```bash
        python collect_mutants.py <techniques> <output_dir>
        ```
        * **Example:**
        
        ```bash
        python collect_mutants.py leam,mubert path/to/output
        ```

    3. Finally, run the ```generate_mutants.py``` script to randomly select mutants
     
    * Use the following command format to run the script:
        
        ```bash
        python generate_mutants.py <techniques> <desired_count> <java_project>
        ```
    
    * **Example:**
        
        ```bash
        python generate_mutants.py leam 600 /path/to/java/projects
        ```
