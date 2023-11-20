# Installations

## Python

[Download Python](https://www.python.org/downloads/)

## PyDrive

[PyDrive](https://pythonhosted.org/PyDrive/) is a Python library for Google Drive API.

```bash
pip install PyDrive
```

# Configuration

## Google Drive API

Client ID and Client Secret can be obtained from [Google API Console](https://console.developers.google.com/).

Download the client configuration file from the Google API Console and save it as **_client_secrets.json_** in your working directory.

Create a file named **_token.json_** in the same directory as your script. This file will store the user’s access and refresh tokens, and is created automatically when the authorization flow completes for the first time.

Here is the structure of my working directory:

```bash
.
|-- README.md
|-- client_secrets.json
|-- main.py
|-- schedule.py
|-- token.json
|-- config.ini
```

In the **_main.py_** file, replace the **_local_folder_path_** and **_drive_folder_id_** with your own values.

### Example of content of config.ini file

```bash
[FOLDER]
LOCAL_FOLDER_PATH  = C:\Users\admin\Desktop\test
DRIVE_FOLDER_ID =0AL9R7YLLZyi_Uk9PVA
IS_SHARE_DRIVE = True
[CONFIG]
DATA_BASE = database.db
[RUN]
IS_RUNNING = 0
[LOG]
LOG_FILE = logs.log
```

# Installation

You need pip to install the required packages.

```bash
pip install -r requirements.txt
```

# How to run :

To execute the script, run the following command:

```bash
python main.py
```

# How work the database :

By default, **_is uploaded_** is set to _null_ for all files. When the file is uploaded to Google Drive, the **_is_uploaded_** is set to 1.

# How to schedule the script :

## Windows

And to schedule the script, follow the steps below:

- Open the Windows Task Scheduler by searching for "Task Scheduler" in the Start menu.

- Click on "Create Task" in the right-hand pane.

- Give your task a name and a description, and then select the "Triggers" tab.
- Click on "New" to create a new trigger.

- Select "Daily" as the trigger type, and choose the time you want the task to run. In this example, we want it to run every day at 3:00 PM.

- Click on the "Actions" tab and then click on "New".
- Select "Start a program" as the action type.

- In the "Program/script" field, enter the path to your Python executable. This is usually something like "C:\Python39\python.exe" (depending on your Python version and installation directory).

- In the "Add arguments" field, enter the path to your Python script. In this example, it would be "C:\path\to\my_script.py".

- Click on "OK" to save the action, and then click on "OK" again to save the task.

- Now your Python script will run automatically based on the trigger you set.

## Linux

You can create a cron job to run a script every minute, hour, day etc. To create a cron job, open a terminal and type:

```bash
crontab -e
```

# To do

- [ ] Add a GUI (Flutter or Electron)
- [ ] Add a log file
- [ ] Add a email notification sender
- [ ] Unit test
