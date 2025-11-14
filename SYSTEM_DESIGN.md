# Messaging Application - System Design Document

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Component Diagram](#component-diagram)
3. [Database Schema](#database-schema)
4. [API Architecture](#api-architecture)
5. [Real-Time Communication Flow](#real-time-communication-flow)
6. [Data Flow Diagram](#data-flow-diagram)
7. [Message Processing Flow](#message-processing-flow)
8. [Deployment Architecture](#deployment-architecture)

---

## System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        A[Agent Portal<br/>HTML/JS]
        C[Customer Form<br/>HTML/JS]
    end
    
    subgraph "Application Layer"
        B[Flask Application<br/>Python]
        W[WebSocket Server<br/>Socket.IO]
    end
    
    subgraph "Business Logic Layer"
        PM[Priority Manager]
        SM[Search Manager]
        CM[Canned Message Manager]
        MM[Message Manager]
    end
    
    subgraph "Data Layer"
        DB[(SQLite Database)]
        E[Excel Files]
    end
    
    A -->|HTTP/WebSocket| B
    C -->|HTTP| B
    B --> W
    B --> PM
    B --> SM
    B --> CM
    B --> MM
    PM --> DB
    SM --> DB
    CM --> DB
    MM --> DB
    MM --> E
```

---

## Component Diagram

```mermaid
graph LR
    subgraph "Frontend Components"
        A1[Agent UI<br/>- Message List<br/>- Message Detail<br/>- Reply Interface]
        A2[Customer Form<br/>- Contact Form<br/>- Message Submission]
    end
    
    subgraph "Backend Services"
        B1[Flask API Server<br/>- REST Endpoints<br/>- Request Handling]
        B2[WebSocket Server<br/>- Real-time Events<br/>- Connection Management]
        B3[Priority Engine<br/>- Keyword Detection<br/>- Priority Calculation]
        B4[Search Engine<br/>- Full-text Search<br/>- Customer Search]
    end
    
    subgraph "Data Services"
        D1[Database ORM<br/>- SQLAlchemy<br/>- Data Models]
        D2[Import Service<br/>- Excel Parser<br/>- Data Migration]
    end
    
    subgraph "Storage"
        S1[(SQLite DB<br/>- Customers<br/>- Messages<br/>- Canned Messages)]
        S2[Excel Files<br/>- Customer Data]
    end
    
    A1 -->|HTTP/WS| B1
    A1 -->|WebSocket| B2
    A2 -->|HTTP| B1
    B1 --> B3
    B1 --> B4
    B1 --> D1
    B2 --> D1
    D1 --> S1
    D2 --> S2
    D2 --> D1
```

---

## Database Schema

```mermaid
erDiagram
    CUSTOMERS ||--o{ MESSAGES : "has"
    MESSAGES }o--|| CUSTOMERS : "belongs to"
    AGENTS ||--o{ MESSAGES : "replies"
    
    CUSTOMERS {
        int id PK
        string name
        string email
        string phone
        string customer_id UK
        datetime created_at
        text profile_data
    }
    
    MESSAGES {
        int id PK
        int customer_id FK
        text content
        string direction
        int agent_id FK
        string agent_name
        string status
        int priority
        datetime created_at
        datetime replied_at
    }
    
    CANNED_MESSAGES {
        int id PK
        string title
        text content
        string category
        datetime created_at
    }
    
    AGENTS {
        int id PK
        string name
        string email
        boolean is_active
        datetime last_active
    }
```

### Database Relationships
- **Customers → Messages**: One-to-Many (One customer can have many messages)
- **Agents → Messages**: One-to-Many (One agent can reply to many messages)
- **Canned Messages**: Standalone table (No foreign keys)

---

## API Architecture

```mermaid
sequenceDiagram
    participant C as Customer
    participant CF as Customer Form
    participant API as Flask API
    participant DB as Database
    participant WS as WebSocket
    participant A as Agent Portal
    
    C->>CF: Submit Message
    CF->>API: POST /api/customers/send-message
    API->>API: Calculate Priority
    API->>DB: Create/Find Customer
    API->>DB: Create Message
    API->>WS: Emit 'new_message'
    WS->>A: Broadcast to Agents
    API-->>CF: Success Response
    CF-->>C: Confirmation
    
    A->>API: GET /api/messages
    API->>DB: Query Messages
    DB-->>API: Message List
    API-->>A: JSON Response
    
    A->>API: GET /api/messages/:id
    API->>DB: Get Message + Customer
    DB-->>API: Message Details
    API-->>A: JSON Response
    
    A->>API: POST /api/messages/:id/reply
    API->>DB: Create Reply Message
    API->>DB: Update Status
    API->>WS: Emit 'new_reply'
    WS->>A: Broadcast Update
    API-->>A: Success Response
```

---

## Real-Time Communication Flow

```mermaid
sequenceDiagram
    participant A1 as Agent 1
    participant A2 as Agent 2
    participant WS as WebSocket Server
    participant API as Flask API
    participant DB as Database
    
    A1->>WS: Connect (Socket.IO)
    A2->>WS: Connect (Socket.IO)
    WS-->>A1: Connected
    WS-->>A2: Connected
    
    Note over API,DB: Customer sends message
    API->>DB: Save Message
    API->>WS: Emit 'new_message'
    WS->>A1: Broadcast 'new_message'
    WS->>A2: Broadcast 'new_message'
    
    A1->>API: Mark as Read
    API->>DB: Update Status
    API->>WS: Emit 'status_update'
    WS->>A2: Broadcast 'status_update'
    
    A1->>API: Send Reply
    API->>DB: Save Reply
    API->>WS: Emit 'new_reply'
    WS->>A1: Broadcast 'new_reply'
    WS->>A2: Broadcast 'new_reply'
```

---

## Data Flow Diagram

```mermaid
flowchart TD
    Start([Customer Sends Message]) --> Input{Input Method}
    Input -->|Web Form| Form[Customer Form UI]
    Input -->|API| API1[POST /api/customers/send-message]
    Form --> API1
    
    API1 --> Validate[Validate Input]
    Validate -->|Invalid| Error1[Return Error]
    Validate -->|Valid| FindCust[Find/Create Customer]
    
    FindCust --> CalcPriority[Calculate Priority<br/>Keyword Detection]
    CalcPriority --> SaveMsg[Save Message to DB]
    
    SaveMsg --> EmitWS[Emit WebSocket Event]
    EmitWS --> Broadcast[Broadcast to All Agents]
    Broadcast --> UpdateUI[Update Agent UIs]
    
    SaveMsg --> Response[Return Success]
    Response --> End([End])
    
    UpdateUI --> AgentView[Agent Views Message]
    AgentView --> MarkRead[Mark as Read]
    MarkRead --> Reply[Agent Replies]
    
    Reply --> SaveReply[Save Reply to DB]
    SaveReply --> UpdateStatus[Update Message Status]
    UpdateStatus --> EmitReply[Emit Reply Event]
    EmitReply --> Broadcast
```

---

## Message Processing Flow

```mermaid
flowchart LR
    subgraph "Message Input"
        M1[Incoming Message]
    end
    
    subgraph "Processing"
        P1[Extract Content]
        P2[Lowercase Conversion]
        P3[Keyword Matching]
        P4[Priority Assignment]
    end
    
    subgraph "Storage"
        S1[Customer Record]
        S2[Message Record]
    end
    
    subgraph "Notification"
        N1[WebSocket Event]
        N2[Agent Notification]
    end
    
    M1 --> P1
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> S1
    P4 --> S2
    S2 --> N1
    N1 --> N2
    
    style P4 fill:#ff9999
    style N2 fill:#99ff99
```

### Priority Detection Algorithm Flow

```
Message Content
    ↓
Convert to Lowercase
    ↓
┌─────────────────────────┐
│ Check High Priority     │
│ Keywords                │
│ (loan approval,         │
│  disbursement, etc.)    │
└─────────────────────────┘
    ↓ (if found)
Priority = 3 (Urgent)
    ↓ (if not found)
┌─────────────────────────┐
│ Check Medium Priority   │
│ Keywords                │
│ (status, update, etc.)  │
└─────────────────────────┘
    ↓ (if found)
Priority = 2 (Medium)
    ↓ (if not found)
┌─────────────────────────┐
│ Check Low Priority      │
│ Keywords                │
│ (how to, change, etc.)  │
└─────────────────────────┘
    ↓ (if found)
Priority = 1 (Low)
    ↓ (if not found)
Priority = 0 (Default)
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Client Devices"
        Browser1[Agent Browser 1]
        Browser2[Agent Browser 2]
        Browser3[Customer Browser]
    end
    
    subgraph "Web Server"
        Flask[Flask Application<br/>Port 5000]
        WS[WebSocket Server<br/>Socket.IO]
    end
    
    subgraph "File System"
        Excel[Excel Files<br/>MessageData*.xlsx]
        Static[Static Files<br/>HTML/CSS/JS]
    end
    
    subgraph "Database"
        SQLite[(SQLite Database<br/>messaging_app.db)]
    end
    
    Browser1 -->|HTTP/WS| Flask
    Browser2 -->|HTTP/WS| Flask
    Browser3 -->|HTTP| Flask
    Flask --> WS
    Flask --> SQLite
    Flask --> Static
    Flask --> Excel
```

---

## System Components Detail

### 1. Frontend Layer

```
┌─────────────────────────────────────┐
│         Agent Portal UI             │
├─────────────────────────────────────┤
│ • Message List Component            │
│ • Message Detail Component          │
│ • Reply Interface Component         │
│ • Search Component                  │
│ • Filter Component                  │
│ • Canned Message Selector           │
│ • Customer Info Display             │
│ • WebSocket Client                  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│        Customer Form UI             │
├─────────────────────────────────────┤
│ • Contact Form                      │
│ • Message Input                     │
│ • Submit Handler                    │
│ • Success/Error Display             │
└─────────────────────────────────────┘
```

### 2. Backend Layer

```
┌─────────────────────────────────────┐
│         Flask Application           │
├─────────────────────────────────────┤
│ • REST API Routes                   │
│ • Request Handlers                  │
│ • Business Logic                    │
│ • Error Handling                    │
│ • CORS Configuration                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      WebSocket Server (Socket.IO)   │
├─────────────────────────────────────┤
│ • Connection Management             │
│ • Event Broadcasting                │
│ • Real-time Updates                 │
│ • Client Synchronization            │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      Business Logic Modules         │
├─────────────────────────────────────┤
│ • Priority Calculator               │
│ • Search Engine                     │
│ • Message Manager                   │
│ • Customer Manager                  │
│ • Canned Message Manager            │
└─────────────────────────────────────┘
```

### 3. Data Layer

```
┌─────────────────────────────────────┐
│      SQLAlchemy ORM                 │
├─────────────────────────────────────┤
│ • Customer Model                    │
│ • Message Model                     │
│ • CannedMessage Model               │
│ • Agent Model                       │
│ • Database Sessions                 │
│ • Query Builder                     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      Data Import Service            │
├─────────────────────────────────────┤
│ • Excel File Reader (Pandas)        │
│ • Column Detection                  │
│ • Data Validation                   │
│ • Duplicate Prevention              │
│ • Batch Insert                      │
└─────────────────────────────────────┘
```

---

## Technology Stack

```
┌─────────────────────────────────────────────┐
│              Technology Stack               │
├─────────────────────────────────────────────┤
│                                             │
│  Frontend:                                  │
│  • HTML5                                    │
│  • CSS3                                     │
│  • Vanilla JavaScript                       │
│  • Socket.IO Client                         │
│                                             │
│  Backend:                                   │
│  • Python 3.x                               │
│  • Flask (Web Framework)                    │
│  • Flask-CORS (CORS Support)                │
│  • Flask-SocketIO (WebSocket)               │
│  • SQLAlchemy (ORM)                         │
│  • Pandas (Data Processing)                 │
│  • OpenPyXL (Excel Reading)                 │
│                                             │
│  Database:                                  │
│  • SQLite (Development)                     │
│  • (PostgreSQL compatible)                  │
│                                             │
│  Real-time:                                 │
│  • Socket.IO                                │
│  • Eventlet (Async Support)                 │
│                                             │
└─────────────────────────────────────────────┘
```

---

## API Endpoint Structure

```
/api
├── /messages
│   ├── GET /                    → List all messages (with filters)
│   ├── GET /<id>                → Get message details
│   ├── POST /<id>/reply         → Reply to message
│   └── POST /<id>/read          → Mark as read
│
├── /customers
│   └── POST /send-message       → Customer sends message
│
├── /canned-messages
│   ├── GET /                    → List all templates
│   └── POST /                   → Create template
│
└── /search
    └── GET /?q=<query>          → Search messages/customers
```

---

## Message Status Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Unread: Customer sends message
    Unread --> Read: Agent opens message
    Read --> Replied: Agent sends reply
    Replied --> [*]
    
    note right of Unread
        Priority calculated
        Visible in agent portal
    end note
    
    note right of Read
        Status updated
        Timestamp recorded
    end note
    
    note right of Replied
        Reply saved
        Conversation updated
    end note
```

---

## Search Flow

```mermaid
flowchart TD
    Start([Agent Types Search Query]) --> Input[Search Input Field]
    Input --> Debounce{Wait 300ms}
    Debounce -->|No Change| Input
    Debounce -->|Query Changed| API[GET /api/search?q=query]
    
    API --> QueryDB[Query Database]
    QueryDB --> SearchMsg[Search Messages<br/>content LIKE query]
    QueryDB --> SearchCust[Search Customers<br/>name/email/phone LIKE query]
    
    SearchMsg --> Combine[Combine Results]
    SearchCust --> Combine
    Combine --> Return[Return JSON]
    Return --> Display[Display Results in UI]
    Display --> End([End])
```

---

## Excel Import Flow

```mermaid
flowchart TD
    Start([Run import_data.py]) --> Scan[Scan Directory]
    Scan --> Find[Find Excel Files<br/>*MessageData*.xlsx]
    Find --> Loop{More Files?}
    
    Loop -->|Yes| Read[Read Excel File<br/>Pandas]
    Read --> Detect[Detect Columns<br/>name, email, message]
    Detect --> Process{More Rows?}
    
    Process -->|Yes| Extract[Extract Row Data]
    Extract --> FindCust[Find/Create Customer]
    FindCust --> CheckDup{Duplicate<br/>Message?}
    
    CheckDup -->|Yes| Process
    CheckDup -->|No| CalcPriority[Calculate Priority]
    CalcPriority --> Save[Save to Database]
    Save --> Process
    
    Process -->|No| Commit[Commit Transaction]
    Commit --> Loop
    
    Loop -->|No| CreateCanned[Create Default<br/>Canned Messages]
    CreateCanned --> End([Import Complete])
```

---

## Security Considerations

```
┌─────────────────────────────────────────────┐
│         Security Architecture               │
├─────────────────────────────────────────────┤
│                                             │
│  Current (Demo):                            │
│  • No authentication (simplified)           │
│  • CORS enabled for development             │
│  • SQL injection protection (ORM)           │
│                                             │
│  Production Recommendations:                │
│  • JWT authentication                       │
│  • Role-based access control                │
│  • Rate limiting                            │
│  • Input validation & sanitization          │
│  • HTTPS/SSL                                │
│  • Environment variables for secrets        │
│  • Database connection pooling              │
│  • SQL injection prevention                 │
│  • XSS protection                           │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Scalability Considerations

```
┌─────────────────────────────────────────────┐
│         Scalability Architecture            │
├─────────────────────────────────────────────┤
│                                             │
│  Current:                                   │
│  • Single server instance                   │
│  • SQLite database                          │
│  • In-memory WebSocket connections          │
│                                             │
│  Horizontal Scaling Options:                │
│  • Load balancer (Nginx)                    │
│  • Multiple Flask instances                 │
│  • Redis for WebSocket pub/sub              │
│  • PostgreSQL for database                  │
│  • Message queue (RabbitMQ/Celery)          │
│  • CDN for static assets                    │
│                                             │
│  Vertical Scaling Options:                  │
│  • Increase server resources                │
│  • Database connection pooling              │
│  • Caching layer (Redis)                    │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Performance Optimization

```
┌─────────────────────────────────────────────┐
│      Performance Optimizations              │
├─────────────────────────────────────────────┤
│                                             │
│  Implemented:                               │
│  • Database indexing on key fields          │
│  • Debounced search input                   │
│  • Efficient SQL queries                    │
│  • WebSocket for real-time (no polling)     │
│                                             │
│  Future Optimizations:                      │
│  • Pagination for message lists             │
│  • Lazy loading of conversations            │
│  • Database query optimization              │
│  • Caching frequently accessed data         │
│  • Compression for API responses            │
│  • CDN for static assets                    │
│                                             │
└─────────────────────────────────────────────┘
```

---

*System Design Document Version 1.0*  
*Last Updated: 2024*

