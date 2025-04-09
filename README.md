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
    
    * Change into the directory where the script is located:
        
        ```bash
        cd path/to/script
        ```

3. **Run the Script**
    
    * Use the following command format to run the script:
        
        ```bash
        python generate_mutants.py <techniques> <desired_mutants_count> <projects_directory>
        ```
    
    * **Parameters:**
        
        * `<techniques>`: A comma-separated list of techniques (e.g., `leam,another_technique`).
            
        * `<desired_mutants_count>`: The number of mutants you want to reproduce (e.g., `600`).
            
        * `<projects_directory>`: The directory path where the projects are located.
            
    * **Example:**
        
        ```bash
        python generate_mutants.py leam 600 /path/to/java/projects
        ```
