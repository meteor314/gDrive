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
`-- token.json
```

In the **_main.py_** file, replace the **_local_folder_path_** and **_drive_folder_id_** with your own values.

```python
# Path: main.py

__local_folder_path__ = r'<Path of  your  folder>'
__drive_folder_id__ = '<ID of the folder in Google Drive>'

```

# How to run :

Open the Windows Task Scheduler by searching for "Task Scheduler" in the Start menu.

Click on "Create Task" in the right-hand pane.

Give your task a name and a description, and then select the "Triggers" tab.
Click on "New" to create a new trigger.

Select "Daily" as the trigger type, and choose the time you want the task to run. In this example, we want it to run every day at 3:00 PM.

Click on the "Actions" tab and then click on "New".
Select "Start a program" as the action type.

In the "Program/script" field, enter the path to your Python executable. This is usually something like "C:\Python39\python.exe" (depending on your Python version and installation directory).

In the "Add arguments" field, enter the path to your Python script. In this example, it would be "C:\path\to\my_script.py".

Click on "OK" to save the action, and then click on "OK" again to save the task.

Now your Python script will run automatically based on the trigger you set.
