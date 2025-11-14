# Messaging Application - Agent Portal

A complete messaging application for customer service agents to respond to incoming customer messages.

## Features

- **Multi-agent Support**: Multiple agents can log in simultaneously
- **Real-time Updates**: New messages appear instantly using WebSockets
- **Priority Detection**: Automatically detects urgent messages (loan approval, disbursement, etc.)
- **Search Functionality**: Search messages and customers
- **Customer Information**: Display customer profiles and context
- **Canned Messages**: Quick response templates for common inquiries
- **Message Management**: View, read, and reply to customer messages

<img width="689" height="442" alt="Screenshot 2025-11-15 at 1 26 52 AM" src="https://github.com/user-attachments/assets/5448c0b2-069d-4995-85cd-2baf0504444b" />

<img width="287" height="640" alt="Screenshot 2025-11-15 at 1 28 56 AM" src="https://github.com/user-attachments/assets/c49d725a-0eb5-4257-88c9-aee6e0d382f5" />


## Setup Instructions

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

Or use the startup script:
```bash
./start.sh
```

### 2. Import Customer Messages

The application includes Excel files with customer messages. Import them into the database:

```bash
python3 import_data.py
```

This will:
- Import all Excel files from the current directory
- Create customer records
- Create message records with priority detection
- Set up default canned messages

### 3. Start the Server

```bash
python3 app.py
```

**Note**: On macOS, use `python3` and `pip3` instead of `python` and `pip`.

The server will start on `http://localhost:5000`

### 4. Access the Application

- **Agent Portal**: Open `agent_ui.html` in your browser (or serve it via a web server)
- **Customer Form**: Open `customer_form.html` in your browser for customers to send messages

## API Endpoints

### Messages
- `GET /api/messages` - Get all messages (supports filters: status, priority, search)
- `GET /api/messages/<id>` - Get message details with conversation history
- `POST /api/messages/<id>/reply` - Reply to a message
- `POST /api/messages/<id>/read` - Mark message as read

### Customer
- `POST /api/customers/send-message` - Send a message from customer

### Canned Messages
- `GET /api/canned-messages` - Get all canned messages
- `POST /api/canned-messages` - Create a new canned message

### Search
- `GET /api/search?q=<query>` - Search messages and customers

## Database Schema

- **Customers**: Customer information and profile data
- **Messages**: Incoming and outgoing messages
- **CannedMessages**: Pre-configured response templates
- **Agents**: Agent information (for future use)

## Priority Detection

Messages are automatically assigned priority based on keywords:
- **High Priority (3)**: loan approval, disbursement, urgent, critical
- **Medium Priority (2)**: status, update, timeline
- **Low Priority (1)**: how to, update information

## Real-time Features

The application uses WebSocket (Socket.IO) for real-time updates:
- New incoming messages appear instantly
- Replies are synchronized across all connected agents
- Connection status indicator in the UI

## Usage Tips

1. **Filter Messages**: Use the filter tabs (All, Unread, Urgent) to focus on specific message types
2. **Search**: Use the search box to find messages by content, customer name, or email
3. **Canned Messages**: Select a canned message from the dropdown to quickly insert a template response
4. **Customer Info**: View customer details and profile information in the message detail view

## API Testing

A Postman collection is included (`Messaging_App_API.postman_collection.json`) for testing the API endpoints. Import it into Postman to test all available endpoints.

## Development Notes

- The application uses SQLite for the database (can be easily switched to PostgreSQL)
- Frontend is built with vanilla HTML/CSS/JavaScript for simplicity
- WebSocket server runs on the same port as the REST API
- Excel files are automatically detected and imported based on filename patterns

