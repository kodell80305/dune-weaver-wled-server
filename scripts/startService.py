import os
import shutil
import sys
import pwd
import grp
import filecmp

# Define the path for the systemd service file
service_file_path = '/etc/systemd/system/dune-weaver-wled.service'
# Use the current working directory
working_directory = os.getcwd()
local_service_file = 'dune-weaver-wled.service'

# Get the current working directory
current_working_directory = os.getcwd()

# Content of the systemd service file
service_file_content = f"""
[Unit]
Description=Dune Weaver WLED Application
After=network.target

[Service]
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/usr/bin/python3 {current_working_directory}/app.py
WorkingDirectory={current_working_directory}
Restart=always
RestartSec=10
StartLimitInterval=0
User=root
Group=root

[Install]
WantedBy=multi-user.target
"""


def check_index_file():
    index_file_path = os.path.join(working_directory, 'templates/index.htm')
    if not os.path.exists(index_file_path):
        print(f"Error: {index_file_path} not found. Running build_web.py...")
        build_web_script = os.path.join(working_directory, 'install_scripts/build_web.py')
        # Get the owner of the working directory
        dir_owner = pwd.getpwuid(os.stat(working_directory).st_uid).pw_name
        # Run build_web.py as the directory owner
        if os.system(f'su -c "python3 {build_web_script}" {dir_owner}') != 0:
            print("Error: Failed to run build_web.py.")
            sys.exit(1)
        if not os.path.exists(index_file_path):
            print(f"Error: {index_file_path} still not found after running build_web.py.")
            sys.exit(1)

def check_and_run_build_web():
    index_file_path = os.path.join(working_directory, 'templates/index.htm')
    if not os.path.exists(index_file_path):
        print(f"Error: {index_file_path} not found. Running build_web.py...")
        build_web_script = os.path.join(working_directory, 'install_scripts/build_web.py')
        dir_owner = pwd.getpwuid(os.stat(working_directory).st_uid).pw_name
        if os.system(f'su -c "python3 {build_web_script}" {dir_owner}') != 0:
            print("Error: Failed to run build_web.py.")
            sys.exit(1)
        return

    # Check if any .js or .py file in the root directory is newer than index.htm
    for file in os.listdir(working_directory):
        if file.endswith('.js') or file.endswith('.py'):
            file_path = os.path.join(working_directory, file)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) > os.path.getmtime(index_file_path):
                print(f"Detected newer file: {file_path}. Running build_web.py...")
                build_web_script = os.path.join(working_directory, 'install_scripts/build_web.py')
                dir_owner = pwd.getpwuid(os.stat(working_directory).st_uid).pw_name
                if os.system(f'su -c "python3 {build_web_script}" {dir_owner}') != 0:
                    print("Error: Failed to run build_web.py.")
                    sys.exit(1)
                return

def install_requirements():
    requirements_file = os.path.join(working_directory, 'requirements.txt')
    marker_file = os.path.join(working_directory, '.requirements_installed')

    # Check if the marker file exists
    if os.path.exists(marker_file):
        print("Requirements already installed. Skipping installation.")
        return

    if os.path.exists(requirements_file):
        print("Installing packages from requirements.txt...")
        if os.system(f'python3 -m pip install --break-system-packages -r {requirements_file}') != 0:
            print("Error: Failed to install required packages.")
            sys.exit(1)
        # Create the marker file to indicate successful installation
        with open(marker_file, 'w') as marker:
            marker.write("Requirements installed.")
    else:
        print("requirements.txt not found. Skipping package installation.")

def create_service():
    # Write the systemd service file locally
    with open(local_service_file, 'w') as service_file:
        service_file.write(service_file_content)

    # Check if the service file exists and if it has changed
    if not os.path.exists(service_file_path) or not filecmp.cmp(local_service_file, service_file_path):
        # Copy the service file to the systemd directory
        shutil.copy(local_service_file, service_file_path)
        print("Systemd service file created/updated successfully.")


    # Reload systemd, enable and start the service
    os.system('systemctl daemon-reload')
    os.system('systemctl enable dune-weaver-wled.service')
    print("Systemd service for Dune Weaver WLED Application has been set up successfully.")

def start_service():
    install_requirements()
    create_service()
    os.system('systemctl start dune-weaver-wled.service')
    print("Systemd service for Dune Weaver WLED Application started.")

def stop_service():
    os.system('systemctl stop dune-weaver-wled.service')
    print("Systemd service for Dune Weaver WLED Application stopped.")

def restart_service():
    stop_service()  # Explicitly stop the service
    start_service()  # Start the service with all necessary checks

def uninstall_service():
    # Stop the service if it is running
    os.system('systemctl stop dune-weaver-wled.service')
    print("Systemd service for Dune Weaver WLED Application stopped.")

    # Disable the service
    os.system('systemctl disable dune-weaver-wled.service')
    print("Systemd service for Dune Weaver WLED Application disabled.")

    # Remove the systemd service file
    if os.path.exists(service_file_path):
        os.remove(service_file_path)
        print("Systemd service file removed.")

    # Reload systemd to apply changes
    os.system('systemctl daemon-reload')
    print("Systemd daemon reloaded.")

    # Remove the local service file if it exists
    if os.path.exists(local_service_file):
        os.remove(local_service_file)
        print("Local service file removed.")

    print("Uninstallation of Dune Weaver WLED Application completed.")

def follow_logs():
    os.system('journalctl -u dune-weaver-wled.service -f')

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python startService.py <start|stop|restart|uninstall> [--follow]")
        sys.exit(1)

    action = sys.argv[1].lower()
    follow = len(sys.argv) == 3 and sys.argv[2] == "--follow"

    if action == "start":
        start_service()
    elif action == "stop":
        stop_service()
    elif action == "restart":
        restart_service()
    elif action == "uninstall":
        uninstall_service()
    else:
        print("Invalid argument. Use 'start', 'stop', 'restart', or 'uninstall'.")
        sys.exit(1)

    if follow and action in {"start", "stop", "restart"}:
        follow_logs()
