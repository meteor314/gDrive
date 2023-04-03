# List how many files are in the folder, and how many are already uploaded is_uploaded=1, and how many are not uploaded is_uploaded0, and how many files are failed to upload is_uploaded=2
import sqlite3
import os

# Connect to the database
conn = sqlite3.connect('uploaded_files.db')
c = conn.cursor()

# Get the number of uploaded files
c.execute("SELECT COUNT(*) FROM uploaded_files WHERE is_uploaded=1")
uploaded_files = c.fetchone()[0]

# Get the number of not uploaded files
c.execute("SELECT COUNT(*) FROM uploaded_files WHERE is_uploaded=0")
not_uploaded_files = c.fetchone()[0]

# Get the number of files that failed to upload
c.execute("SELECT COUNT(*) FROM uploaded_files WHERE is_uploaded=2")
failed_files = c.fetchone()[0]

# Print the results
print(f"Uploaded files: {uploaded_files}")
print(f"Not uploaded files: {not_uploaded_files}")
print(f"Failed files: {failed_files}")

# Close the connection
conn.close()
