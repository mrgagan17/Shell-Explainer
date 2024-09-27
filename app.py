import sqlite3
from flask import Flask, render_template, request, redirect, flash
import bashlex  # Ensure bashlex is installed via pip
app = Flask(__name__)
app.secret_key = 'your_secret_key'






# Dictionary for command explanations
explanations = {
    'ls': 'Lists files and directories in the current directory.\n[1) ls -l: Use a long listing format,   2) ls -a: Includes hidden files (those starting with .),   3) ls -h: Human-readable sizes (e.g., KB, MB),   4) ls -R: Recursive listing,  5) ls -t: Sort by modification time,   6) ls -S: Sort by file size,   7) ls -r: Reverse order while sorting,   8) ls -i: Print the index number of each file].',
    'cd': 'Change directory. [1) cd ..: Moves one directory up (to the parent directory), 2) cd ~: Moves to the home directory.]',
    'mkdir': 'Make directories. [1) -p: Create parent directories as needed, 2) -m: Set permissions for the new directories, 3) -v: Display the process of creating directories.]',
    'rm': 'Remove files or directories. [1) -f: Force removal without prompting, 2) -i: Prompts for confirmation before each file is removed,  3) -r: Removes directories and their contents recursively. This is necessary to delete non-empty directories,  4) -d: Removes empty directories,  5) -v: Provides a detailed output of the rm command’s actions, showing the names of files and directories as they are removed.]',
    'cp': 'Copy files or directories.  [1) -a: Archive mode (preserve attributes, recursive),  2) Recursive copy of directories,  3) -i: Interactive (prompt before overwriting),  4) -u: Update (copy only if source is newer or missing),  5) -v: Verbose (show files being copied),  6) -p: Preserve file attributes,  7) -f: Force overwrite of destination files.]',
    'mv': 'Move or rename files or directories  [1) mv file1 file2: Renames or moves file1 to file2, 2) mv dir1/ /path/to/: Moves dir1 to the specified path, 3) mv -i file1 file2: Prompts before overwriting file2]',
    'cat': 'Concatenate and display files  [1) cat file: Displays the content of file, 2) cat file1 file2: Concatenates and displays content of file1 and file2, 3) cat > file: Redirects input to file]',
    'grep': 'Search text using patterns  [1) grep pattern file: Searches for pattern in file, 2) grep -i pattern file: Ignores case distinctions, 3) grep -r pattern dir: Recursively searches in directory dir, 4) grep -v pattern file: Inverts the match, showing lines that do not match the pattern]',
    'find': 'Search for files in a directory hierarchy  [1) find -name file: Searches for file in /path, 2) find -type d: Searches for directories in /path, 3) find -mtime -7: Finds files modified in the last 7 days, 4) find -size +1M: Finds files larger than 1 MB]',
    'echo': 'Display a line of text  [1) echo -n: Displays the text without a trailing newline, 2) echo -e : Enables interpretation of backslash escapes (e.g., \n for a new line), 3) echo -E text: Disables interpretation of backslash escapes (default behavior), 4) echo $VARIABLE: Displays the value of the environment variable, 5) echo "text with spaces": Preserves spaces in the text]',
    'chmod': 'Change file mode bits  [1) chmod 755 file: Sets permissions to rwxr-xr-x, 2) chmod +x file: Adds execute permission, 3) chmod -r 644 dir: Recursively sets permissions for files in dir, 4) chmod u+x file: Adds execute permission for the file owner]',
    'ps': 'Report process status  [1) ps aux: Shows all processes with detailed information, 2) ps -ef: Displays processes in a full-format listing, 3) ps -u user: Shows processes for a specific user]',
    'top': 'Task manager  [1) top: Displays a dynamic real-time view of system processes, 2) top -u user: Displays processes for a specific user, 3) top -d 5: Updates the display every 5 seconds]',
    'pwd': 'Print working directory  [1) pwd: Displays the full path of the current working directory, 2) pwd -L: Prints the logical current working directory (resolves symbolic links), 3) pwd -P: Prints the physical current working directory (shows the actual path without symbolic links)]',
    'man': 'Display the manual for a command  [1) man command: Displays the manual page for "command", 2) man -k keyword: Searches the manual page database for "keyword", 3) man -f command: Displays a short description of "command", 4) man -a command: Displays all available manual pages for "command", 5) man -l file: Displays the manual page from a local file, 6) man section command: Displays the manual page from a specific section (e.g., 1 for user commands, 5 for file formats)]',
    'df': 'Report file system disk space usage  [1) df: Displays disk space usage for all mounted file systems, 2) df -h: Shows disk space in human-readable format (e.g., MB, GB), 3) df -T: Displays the type of each file system, 4) df -i: Shows information about inode usage, 5) df --total: Displays a grand total of disk space usage for all file systems]',
    'du': 'Estimate file space usage  [1) du: Displays the disk usage of the current directory and its subdirectories, 2) du -h: Shows disk usage in human-readable format (e.g., KB, MB, GB), 3) du -s: Displays only the total size of each argument, 4) du -a: Includes files in the output (not just directories), 5) du -c: Provides a grand total of disk usage, 6) du --max-depth=N: Limits the depth of directory traversal (e.g., 1 for top level only)]',
    'tar': 'Archive files  [1) tar -cvf archive.tar file1 file2: Creates a new archive "archive.tar" with "file1" and "file2", 2) tar -xvf archive.tar: Extracts files from "archive.tar", 3) tar -tvf archive.tar: Lists the contents of "archive.tar", 4) tar -czvf archive.tar.gz file1 file2: Creates a compressed archive "archive.tar.gz" using gzip, 5) tar -xzvf archive.tar.gz: Extracts files from a gzip-compressed archive, 6) tar -cjf archive.tar.bz2 file1 file2: Creates a compressed archive "archive.tar.bz2" using bzip2, 7) tar -xjvf archive.tar.bz2: Extracts files from a bzip2-compressed archive, 8) tar -cf archive.tar --exclude=pattern file1 file2: Creates an archive excluding files matching "pattern"]',
    'gzip': 'Compress files  [1) gzip file: Compresses "file" and replaces it with "file.gz", 2) gzip -d file.gz: Decompresses "file.gz" and restores the original "file", 3) gzip -c file: Compresses "file" and writes the output to standard output (stdout), 4) gzip -k file: Compresses "file" and keeps the original "file", 5) gzip -r dir: Recursively compresses all files in the directory "dir", 6) gzip -t file.gz: Tests the integrity of the compressed file "file.gz"]',
    'gunzip': 'Decompress files  [1) gunzip file.gz: Decompresses file.gz and restores the original file, 2) gunzip -c file.gz: Decompresses file.gz and writes the output to standard output (stdout), 3) gunzip -k file.gz: Decompresses file.gz and keeps the original file.gz, 4) gunzip -r dir: Recursively decompresses all files in the directory dir, 5) gunzip -t file.gz: Tests the integrity of the compressed file file.gz]',
    'zip': 'Package and compress files  [1) zip archive.zip files: Create archive, 2) zip -r archive.zip dir: Recursively add directory, 3) zip -e archive.zip file: Encrypt archive, 4) zip -d archive.zip file: Delete from archive, 5) zip -u archive.zip file: Update archive]',
    'unzip': 'Extract compressed files  [1) unzip archive.zip: Extracts files, 2) unzip -d dir archive.zip: Extracts to "dir", 3) unzip -l archive.zip: Lists contents, 4) unzip -o archive.zip: Overwrites files, 5) unzip -t archive.zip: Tests archive]',
    'wget': 'Download files from the web  [1) wget url: Download from URL, 2) wget -O file url: Save as "file", 3) wget -r url: Recursive download, 4) wget -c url: Resume download, 5) wget -q url: Quiet mode]',
    'curl': 'Transfer data from or to a server  [1) curl url: Fetch content from URL, 2) curl -o file url: Save as "file", 3) curl -O url: Save with original name, 4) curl -I url: Get headers only, 5) curl -L url: Follow redirects]',
    'ssh': 'OpenSSH remote login client  [1) ssh user@host: Connect to "host" as "user", 2) ssh -i key user@host: Use "key" for authentication, 3) ssh -p port user@host: Connect using "port", 4) ssh -X user@host: Enable X11 forwarding, 5) ssh -T user@host: Disable pseudo-terminal allocation]',
    'scp': 'Secure copy (remote file copy)  [1) scp file user@host:/path: Copy file to remote host, 2) scp user@host:/path/file: Copy file from remote host, 3) scp -r dir user@host:/path: Recursively copy directory, 4) scp -P port file user@host:/path: Use "port" for connection, 5) scp -i key file user@host:/path: Use "key" for authentication]',
    'rsync': 'Remote file and directory synchronization  [1) rsync source dest: Syncs "source" to "dest", 2) rsync -r source/ dest/: Recursively copy directories, 3) rsync -a source/ dest/: Archive mode (preserves attributes), 4) rsync -v source/ dest/: Verbose output, 5) rsync -z source/ dest/: Compress during transfer]',
    'kill': 'Send signals to processes  [1) kill PID: Send default SIGTERM to process with "PID", 2) kill -9 PID: Forcefully kill process with "PID", 3) kill -l: List all signal names]',
    'pkill': 'Send signals to processes by name  [1) pkill name: Send default SIGTERM to processes named "name", 2) pkill -9 name: Forcefully kill processes named "name", 3) pkill -u user name: Kill processes named "name" owned by "user"]',
    'jobs': 'List active jobs  [1) jobs: Show list of jobs, 2) jobs -l: Show detailed job information]',
    'bg': 'Resume a suspended job in the background  [1) bg %job: Resume job "job" in the background]',
    'fg': 'Bring a job to the foreground  [1) fg %job: Bring job "job" to the foreground, 2) fg: Bring the most recent background job to the foreground]',
    'history': 'Show command history  [1) history: Show command history, 2) history N: Show last "N" commands, 3) history -c: Clear the history list]',
    'alias': 'Create an alias for a command  [1) alias name="command": Create an alias "name" for "command", 2) alias: List all current aliases]',
    'unalias': 'Remove an alias  [1) unalias name: Remove the alias "name", 2) unalias -a: Remove all aliases]',
    'sudo': 'Execute a command as another user  [1) sudo command: Run "command" as superuser, 2) sudo -s: Start a shell with superuser privileges, 3) sudo -u user command: Run "command" as "user"]',
    'chmod': 'Change file permissions  [1) chmod 755 file: Set permissions to "rwxr-xr-x", 2) chmod +x file: Add execute permission, 3) chmod -R 755 dir: Recursively set permissions on directory "dir"]',
    'chown': 'Change file owner and group  [1) chown user file: Change owner of "file" to "user", 2) chown user:group file: Change owner and group of "file", 3) chown -R user dir: Recursively change ownership of directory "dir"]',
    'groupadd': 'Add a new group  [1) groupadd group: Add a new group named "group", 2) groupadd -g gid group: Create a group with specified GID "gid"]',
    'useradd': 'Add a new user  [1) useradd username: Create a new user "username", 2) useradd -m username: Create user with a home directory, 3) useradd -s shell username: Set login shell for "username"]',
    'usermod': 'Modify a user account  [1) usermod -aG group username: Add "username" to group "group", 2) usermod -s shell username: Change login shell for "username", 3) usermod -d home username: Change home directory for "username"]',
    'passwd': 'Change user password  [1) passwd username: Change password for "username", 2) passwd: Change the current users password]',
    'date': 'Display or set the system date and time  [1) date: Show current date and time, 2) date "+%Y-%m-%d": Display date in YYYY-MM-DD format, 3) date MMDDhhmm[[CC]YY][.ss]: Set date and time]',
    'cal': 'Display a calendar  [1) cal: Show current months calendar, 2) cal -y: Show calendar for the current year, 3) cal 2024: Show calendar for the year 2024]',
    'uptime': 'Show how long the system has been running  [1) uptime: Display how long the system has been running, 2) uptime -p: Show uptime in a human-readable format]',
    'top': 'Display system processes and resource usage  [1) top: Display real-time system statistics and processes, 2) top -d seconds: Update display every "seconds", 3) top -u user: Show processes for "user"]',
    'htop': 'Interactive process viewer (requires installation)  [1) htop: Display real-time system processes with interactive interface, 2) htop -d seconds: Set delay between updates to "seconds", 3) htop -u user: Show processes for "user"]',
    'iostat': 'Report CPU and I/O statistics  [1) iostat: Show CPU and I/O statistics, 2) iostat -x: Display extended statistics, 3) iostat -d 5: Report every 5 seconds]',
    'vmstat': 'Report virtual memory statistics  [1) vmstat: Display system memory, processes, and I/O statistics, 2) vmstat 5: Report every 5 seconds, 3) vmstat -s: Display a summary of memory statistics]',
    'dmesg': 'Print kernel ring buffer messages  [1) dmesg: Show kernel ring buffer messages, 2) dmesg -T: Display timestamps with messages, 3) dmesg | grep keyword: Search messages for "keyword"]',
    'logname': 'Print the user name of the current user  [1) logname: Display the login name of the user who started the session]',
    'uname': 'Print system information  [1) uname: Show kernel name, 2) uname -a: Show all system information (kernel, hostname, etc.), 3) uname -r: Show kernel release]',
    'hostname': 'Show or set the systems hostname  [1) hostname: Display the current hostname, 2) hostname newname: Set the hostname to "newname"]',
    'ping': 'Send ICMP ECHO_REQUEST to network hosts  [1) ping host: Send ICMP echo requests to "host", 2) ping -c count host: Send "count" number of pings, 3) ping -t ttl host: Set the TTL value]',
    'traceroute': 'Print the route packets take to a network host [1) traceroute host: Show the path packets take to "host", 2) traceroute -m max_ttl host: Set maximum number of hops to "max_ttl"]',
    'netstat': 'Print network connections, routing tables, interface statistics  [1) netstat: Show network connections, 2) netstat -t: Display TCP connections, 3) netstat -u: Display UDP connections, 4) netstat -r: Show routing table]',
    'ifconfig': 'Configure network interfaces (deprecated, use `ip` instead)  [1) ifconfig: Show network interfaces, 2) ifconfig interface: Show details for "interface", 3) ifconfig interface up: Activate "interface", 4) ifconfig interface down: Deactivate "interface"]',
    'ip': 'Show/manipulate routing, devices, policy routing and tunnels  [1) ip a: Show all IP addresses, 2) ip link: Show network interfaces, 3) ip route: Show routing table, 4) ip addr add address dev interface: Assign IP address to "interface", 5) ip link set interface up/down: Activate/deactivate "interface"]',
    'route': 'Show/manipulate the IP routing table  [1) route: Show current routing table, 2) route add destination gateway: Add a route to "destination" via "gateway", 3) route del destination: Remove route to "destination"]',
    'systemctl': 'Control the systemd system and service manager  [1) systemctl start service: Start "service", 2) systemctl stop service: Stop "service", 3) systemctl restart service: Restart "service", 4) systemctl status service: Show status of "service", 5) systemctl enable service: Enable "service" to start at boot, 6) systemctl disable service: Disable "service" from starting at boot]',
    'journalctl': 'Query and display messages from the journal  [1) journalctl: Show all logs, 2) journalctl -u service: Show logs for "service", 3) journalctl -f: Follow logs in real-time, 4) journalctl --since "time": Show logs since "time", 5) journalctl --until "time": Show logs until "time"]',
    'service': 'Run a System V init script  [1) service service start: Start "service", 2) service service stop: Stop "service", 3) service service restart: Restart "service", 4) service service status: Show status of "service"]',
    'update': 'Update package lists (Debian-based systems)  [1) apt update: Refresh package index on Debian-based systems, 2) yum update: Upgrade all installed packages on RPM-based systems, 3) dnf update: Upgrade all installed packages on RPM-based systems, 4) brew update: Fetch the latest version of Homebrew and its formulae]',
    'upgrade': 'Upgrade installed packages (Debian-based systems)  [1) apt upgrade: Upgrade installed packages to their latest versions]',
    'yum': 'Package manager (RHEL-based systems)  [1) yum update: Update all packages to the latest versions, 2) yum install package: Install "package", 3) yum remove package: Remove "package", 4) yum list installed: List installed packages]',
    'dnf': 'Package manager (Fedora-based systems)  [1) dnf update: Update all packages to the latest versions, 2) dnf install package: Install "package", 3) dnf remove package: Remove "package", 4) dnf list installed: List installed packages]',
    'apt': 'Package manager (Debian-based systems)  [1) apt update: Update package list, 2) apt upgrade: Upgrade all installed packages, 3) apt install package: Install "package", 4) apt remove package: Remove "package", 5) apt list --installed: List installed packages]',
    'brew': 'Package manager for macOS  [1) brew update: Update Homebrew and package lists, 2) brew upgrade: Upgrade all installed packages, 3) brew install package: Install "package", 4) brew uninstall package: Uninstall "package", 5) brew list: List installed packages]',
   
}


# Function to get explanation for each part of the command
def get_explanation(part):
    return explanations.get(part, f"Unknown command: {part}")

# Initialize database
def init_db():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT, message TEXT)''')
    conn.commit()
    conn.close()

# Route to show the form for user input
@app.route('/')
def index():
    return render_template('index.html')

# Handle contact form submissions
@app.route('/submit_message', methods=['POST'])
def submit_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Save message to the database
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)", (name, email, message))
    conn.commit()
    conn.close()

    flash('Message sent successfully!')
    return redirect('/contact')
    

# Admin route to view messages
@app.route('/admin/messages')
def view_messages():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("SELECT * FROM messages")
    messages = c.fetchall()
    conn.close()
    return render_template('admin_messages.html', messages=messages)

# Route to process the command and return explanations
@app.route('/explain', methods=['POST'])
def explain():
    command = request.form.get('command')  # Get command input from the user
    parts = bashlex.split(command)         # Split the command into parts using bashlex
    explanation = " | ".join([get_explanation(part) for part in parts])  # Join explanations
    return render_template('index.html', command=command, explanation=explanation)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)






