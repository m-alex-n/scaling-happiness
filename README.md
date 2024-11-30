# VCS



This code implements a simple version control system (VCS) that allows users to initialize a repository, stage files, commit changes, and view commit history via a command-line interface. The system organizes its data in a directory structure, using SHA-1 hashing to uniquely identify file contents and commits. Key functions include init() for setting up the repository, add() for staging files while checking against an ignore list, commit() for creating new commits with metadata, and log() for displaying the commit history. The program leverages JSON for storing the index and commit data, making it a foundational example of how version control systems like Git operate. 
