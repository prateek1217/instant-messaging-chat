# Messaging Application - Project Documentation

## Project Overview

A complete customer service messaging platform that enables multiple agents to respond to incoming customer messages in real-time. The system automatically prioritizes urgent messages, provides search capabilities, and includes canned responses for efficient customer support.

---

## Core Functionalities

### 1. Multi-Agent Support System
**What it does:** Allows multiple customer service agents to log in simultaneously and work on different messages.

**How it works:**
- No authentication required (simplified for demo)
- Multiple agents can access the portal at the same time
- Each agent can view, read, and respond to messages independently
- Real-time synchronization ensures all agents see the latest messages

**Technical Implementation:**
- WebSocket-based real-time updates
- Agent ID tracking for message replies
- Concurrent session support

---

### 2. Customer Message Reception
**What it does:** Receives and stores incoming messages from customers via API or web form.

**How it works:**
- Customers submit messages through a web form or API endpoint
- System automatically creates customer records if they don't exist
- Messages are stored in the database with timestamps
- Priority is automatically calculated based on message content

**Technical Implementation:**
- REST API endpoint: `POST /api/customers/send-message`
- Customer form UI at `/customer`
- Automatic customer record creation
- Message priority detection on submission

---

### 3. Automatic Priority Detection
**What it does:** Automatically identifies and flags urgent messages that need immediate attention.

**How it works:**
- Scans message content for urgency keywords
- Assigns priority levels: High (3), Medium (2), Low (1), Default (0)
- High priority keywords: loan approval, disbursement, urgent, emergency, etc.
- Messages are sorted by priority in the agent interface

**Priority Levels:**
- **Priority 3 (Urgent):** Loan approval, disbursement, urgent, emergency, critical
- **Priority 2 (Medium):** Status inquiries, timeline questions, updates
- **Priority 1 (Low):** How-to questions, account modifications
- **Priority 0 (Default):** General inquiries

**Technical Implementation:**
- Keyword-based detection algorithm
- Case-insensitive matching
- Highest priority keyword determines final priority

---

### 4. Message Management Interface
**What it does:** Provides agents with a comprehensive interface to view, filter, and manage customer messages.

**How it works:**
- Message list sidebar shows all incoming messages
- Filter options: All, Unread, Urgent
- Click on any message to view full conversation
- Visual indicators for unread and high-priority messages
- Conversation history displayed chronologically

**Features:**
- Unread message highlighting
- Priority badges (Urgent, Medium)
- Timestamp display
- Customer name and preview

**Technical Implementation:**
- REST API: `GET /api/messages` with filter parameters
- Real-time updates via WebSocket
- Client-side filtering and sorting

---

### 5. Search Functionality
**What it does:** Enables agents to quickly find specific messages or customers.

**How it works:**
- Search box in the agent interface
- Searches across message content, customer names, and email addresses
- Real-time search results as you type
- Returns matching messages and customer records

**Search Scope:**
- Message content
- Customer name
- Customer email
- Customer phone number

**Technical Implementation:**
- API endpoint: `GET /api/search?q=<query>`
- SQL LIKE queries across multiple tables
- Debounced search input (300ms delay)

---

### 6. Customer Information Display
**What it does:** Shows relevant customer context to help agents provide personalized support.

**How it works:**
- Displays customer profile when viewing a message
- Shows: Name, Email, Phone, Customer ID
- Includes additional profile data (account type, join date, etc.)
- Provides context for better customer service

**Displayed Information:**
- Basic contact details
- Customer ID
- Account type (premium/standard)
- Account creation date
- Message history count

**Technical Implementation:**
- Customer data stored in database
- Profile data as JSON field
- Fetched with message details via `GET /api/messages/<id>`

---

### 7. Message Response System
**What it does:** Allows agents to reply to customer messages and maintain conversation history.

**How it works:**
- Reply textarea in message detail view
- Send button to submit response
- Replies are stored as outgoing messages
- Original message status updated to "replied"
- Full conversation history displayed chronologically

**Features:**
- Rich text input area
- Agent name attached to replies
- Timestamp tracking
- Status updates (unread → read → replied)

**Technical Implementation:**
- API endpoint: `POST /api/messages/<id>/reply`
- Message direction tracking (incoming/outgoing)
- Status field updates
- Real-time broadcast to all connected agents

---

### 8. Canned Messages Feature
**What it does:** Provides pre-written response templates for common customer inquiries.

**How it works:**
- Dropdown menu with pre-configured messages
- Select a template to auto-fill the reply box
- Agents can edit before sending
- Organized by categories (loan, account, general)

**Default Templates:**
- Loan Approval Status
- Loan Disbursement Timeline
- Update Account Information
- General Inquiry
- Password Reset

**Technical Implementation:**
- Database table: `canned_messages`
- API endpoint: `GET /api/canned-messages`
- Dropdown selection populates textarea
- Editable before sending

---

### 9. Real-Time Updates
**What it does:** Ensures all agents see new messages and replies instantly without page refresh.

**How it works:**
- WebSocket connection between client and server
- Server broadcasts new messages to all connected clients
- Automatic UI updates when new messages arrive
- Connection status indicator

**Events:**
- `new_message`: Broadcasts when customer sends a message
- `new_reply`: Broadcasts when agent replies
- `connect/disconnect`: Connection status tracking

**Technical Implementation:**
- Socket.IO for WebSocket communication
- Event-driven architecture
- Automatic reconnection on disconnect
- Fallback polling every 30 seconds

---

### 10. Message Status Tracking
**What it does:** Tracks the state of each message (unread, read, replied) for workflow management.

**How it works:**
- Messages start as "unread"
- Automatically marked "read" when agent opens message
- Changed to "replied" when agent sends response
- Status visible in message list

**Status Flow:**
- `unread` → `read` → `replied`

**Technical Implementation:**
- Status field in messages table
- API endpoint: `POST /api/messages/<id>/read`
- Automatic status update on message view
- Visual indicators in UI

---

### 11. Excel Data Import
**What it does:** Bulk imports customer messages from Excel files into the database.

**How it works:**
- Scans directory for Excel files with "MessageData" in filename
- Automatically detects columns (name, email, message, etc.)
- Creates customer records if they don't exist
- Imports messages with priority detection
- Prevents duplicate imports

**Import Process:**
1. Read Excel file
2. Identify columns (name, email, phone, message)
3. Create/find customer record
4. Create message with priority calculation
5. Skip duplicates

**Technical Implementation:**
- Python script: `import_data.py`
- Pandas for Excel reading
- SQLAlchemy for database operations
- Duplicate detection logic

---

## Technical Architecture

### Backend
- **Framework:** Flask (Python)
- **Database:** SQLite (easily switchable to PostgreSQL)
- **Real-time:** Socket.IO (WebSocket)
- **ORM:** SQLAlchemy

### Frontend
- **Technology:** Vanilla HTML/CSS/JavaScript
- **Real-time:** Socket.IO client library
- **Styling:** Modern CSS with responsive design

### Database Schema
- **customers:** Customer information and profiles
- **messages:** Incoming and outgoing messages
- **canned_messages:** Response templates
- **agents:** Agent information (for future use)

---

## API Endpoints

### Messages
- `GET /api/messages` - List all messages (with filters)
- `GET /api/messages/<id>` - Get message details with conversation
- `POST /api/messages/<id>/reply` - Reply to a message
- `POST /api/messages/<id>/read` - Mark message as read

### Customer
- `POST /api/customers/send-message` - Customer sends a message

### Canned Messages
- `GET /api/canned-messages` - Get all templates
- `POST /api/canned-messages` - Create new template

### Search
- `GET /api/search?q=<query>` - Search messages and customers

---

## Key Features Summary

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Multi-Agent** | Multiple agents work simultaneously | Scalable support team |
| **Priority Detection** | Auto-identifies urgent messages | Faster response to critical issues |
| **Real-Time Updates** | Instant message synchronization | No page refresh needed |
| **Search** | Find messages/customers quickly | Efficient message retrieval |
| **Canned Messages** | Pre-written response templates | Faster response times |
| **Customer Context** | View customer profile and history | Personalized support |
| **Conversation History** | Full message thread view | Better context understanding |
| **Status Tracking** | Track message workflow | Better team coordination |

---

## Setup & Usage

### Quick Start
1. Install dependencies: `pip3 install -r requirements.txt`
2. Import data: `python3 import_data.py`
3. Start server: `python3 app.py`
4. Access:
   - Agent Portal: `http://localhost:5000/agent`
   - Customer Form: `http://localhost:5000/customer`

### Data Import
- Place Excel files in project directory
- Run `python3 import_data.py`
- System auto-detects and imports all "MessageData" Excel files

---

## Workflow Example

1. **Customer sends message** → Stored in database with priority
2. **Message appears in agent portal** → Real-time update
3. **Agent views message** → Status changes to "read"
4. **Agent selects canned message** → Template fills reply box
5. **Agent sends reply** → Message marked as "replied"
6. **Customer receives response** → Conversation continues

---

## Future Enhancements (Potential)

- User authentication and role management
- Advanced analytics and reporting
- Message assignment to specific agents
- Email/SMS notifications
- Integration with external CRM systems
- Machine learning for better priority detection
- Multi-language support
- File attachments support

---

*Document Version: 1.0*  
*Last Updated: 2024*

