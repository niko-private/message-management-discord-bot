# message-management-discord-bot

A Python and MongoDB-based Discord bot for storing, managing, retrieving, and displaying messages and attachments. With multiple features designed for ease of use.

**Invite the bot to your server:** [[Pokes](https://discord.com/oauth2/authorize?client_id=1313108637782249503&permissions=8&integration_type=0&scope=bot)]  

## Setup

1. Clone the repository or download the files to your local machine or server.
   
2. **Install requirements**  
   Ensure you have Python 3.x installed. Then, install the necessary Python libraries:
   ```bash
   pip install -r requirements.txt
   ```
3. **Setup the `.env`**  
    In the bot/ directory, create a .env file and add the following details:
    ```env
    DISCORD_TOKEN=your_token_here # Essential
    MONGODB_STRING=your_mongo_connection_string_here # Essential
    AUTHOR_ID=your_discord_id_here # Allowing the sync
    SPECIAL_USER=your_special_user_id_here # Special message, irrelevant
    SPECIAL_PHRASE=your_special_phrase_here # Special message, irrelevant
    ```

## Usage
### `/store`  
Store a message id with a specified file name. Parameters: `name` (str) - File name, `id` (str) - Message ID.  
Example: `/store name="example_name" id="123456789012345678"`
### `/make`  
Create a folder with a specified name. Parameters: `name` (str) - Folder name to create.  
Example: `/make name="example_folder"`
### `/save`  
Save a specified number of messages from a channel (max = 100). Parameters: `channel` (TextChannel) - Channel to fetch messages from, `limit` (int) - Number of messages to save.  
Example: `/save channel="#general" limit=50`
### `/show`  
Show the content of a specified file. Parameters: `name` (str) - File name to display the content of.  
Example: `/show name="example_file"`
### `/repeat`  
Show the content of a specified file multiple times. Parameters: `name` (str) - File name to display, `times` (int) - Number of times to display the message.  
Example: `/repeat name="example_file" times=3`
### `/random`  
Get a random line or message from a file or folder. Parameters: `name` (str) - File or folder name to retrieve a random item from.  
Example: `/random name="example_file"`
### `/get`  
Get a link to a specified file. Parameters: `name` (str) - File name to get the link for.  
Example: `/get name="example_file"`
### `/set`  
Set a channel for messages to be sent to. Parameters: `channel` (str, optional) - The channel to show stored messages in.  
Example: `/set channel="general"`
### `/rename`  
Rename a file to a new name. Parameters: `file_name` (str) - Current file name, `new_name` (str) - New file name.  
Example: `/rename file_name="old_name" new_name="new_name"`
### `/move`  
Move files to a specified folder. Parameters: `files` (str) - Comma-separated list of files to move, `folder_name` (str, optional) - Destination folder.  
Example: `/move files="file1,file2,file3" folder_name="new_folder"`
### `/delete`  
Delete specified files. Parameters: `files` (str) - Comma-separated list of files to delete.  
Example: `/delete files="file1,file2,file3"`
### `/offer`  
Offer a file or files to a user. Parameters: `name` (discord.User) - User to send file to, `file_name` (str) - File name to offer.  
Example: `/offer name="User" file_name="file1"`
### `/accept`  
Accept an offer made by another user. Parameters: `name` (discord.User) - User who offered the file, `append_name` (str) - Append to the file name.  
Example: `/accept name="User" append_name="new_version"`
### `/paginate`  
Paginate through stored items.  
Example: `/paginate`


