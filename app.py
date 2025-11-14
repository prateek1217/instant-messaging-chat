from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///messaging_app.db', echo=False)
Session = sessionmaker(bind=engine)

# Database Models
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    email = Column(String(200))
    phone = Column(String(50))
    customer_id = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="customer")
    profile_data = Column(Text)  # JSON string for additional customer info

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    customer = relationship("Customer", back_populates="messages")
    content = Column(Text)
    direction = Column(String(20))  # 'incoming' or 'outgoing'
    agent_id = Column(Integer, nullable=True)  # Null for incoming, set for outgoing
    agent_name = Column(String(100), nullable=True)
    status = Column(String(20), default='unread')  # 'unread', 'read', 'replied'
    priority = Column(Integer, default=0)  # Higher number = more urgent
    created_at = Column(DateTime, default=datetime.utcnow)
    replied_at = Column(DateTime, nullable=True)

class CannedMessage(Base):
    __tablename__ = 'canned_messages'
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    content = Column(Text)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(200))
    is_active = Column(Boolean, default=True)
    last_active = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(engine)

# Urgency keywords for priority detection
URGENCY_KEYWORDS = {
    'high': ['loan approval', 'loan disbursed', 'disbursement', 'approval process', 
             'urgent', 'asap', 'immediately', 'critical', 'emergency'],
    'medium': ['status', 'update', 'when', 'how long', 'timeline'],
    'low': ['how to', 'update information', 'change', 'modify']
}

def calculate_priority(content):
    """Calculate message priority based on content"""
    content_lower = content.lower()
    priority = 0
    
    for keyword in URGENCY_KEYWORDS['high']:
        if keyword in content_lower:
            priority = max(priority, 3)
    
    for keyword in URGENCY_KEYWORDS['medium']:
        if keyword in content_lower:
            priority = max(priority, 2)
    
    for keyword in URGENCY_KEYWORDS['low']:
        if keyword in content_lower:
            priority = max(priority, 1)
    
    return priority

# API Routes
@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all messages with optional filters"""
    session = Session()
    try:
        status = request.args.get('status', 'all')
        priority = request.args.get('priority', None)
        search = request.args.get('search', '')
        
        query = session.query(Message).filter(Message.direction == 'incoming')
        
        if status != 'all':
            query = query.filter(Message.status == status)
        
        if priority:
            query = query.filter(Message.priority >= int(priority))
        
        if search:
            query = query.join(Customer).filter(
                (Message.content.contains(search)) |
                (Customer.name.contains(search)) |
                (Customer.email.contains(search))
            )
        
        messages = query.order_by(Message.priority.desc(), Message.created_at.desc()).all()
        
        result = []
        for msg in messages:
            result.append({
                'id': msg.id,
                'customer_id': msg.customer_id,
                'customer_name': msg.customer.name if msg.customer else 'Unknown',
                'customer_email': msg.customer.email if msg.customer else '',
                'content': msg.content,
                'status': msg.status,
                'priority': msg.priority,
                'created_at': msg.created_at.isoformat(),
                'replied_at': msg.replied_at.isoformat() if msg.replied_at else None
            })
        
        return jsonify(result)
    finally:
        session.close()

@app.route('/api/messages/<int:message_id>', methods=['GET'])
def get_message(message_id):
    """Get a specific message with customer details"""
    session = Session()
    try:
        message = session.query(Message).filter(Message.id == message_id).first()
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        customer = message.customer
        customer_info = {}
        if customer:
            customer_info = {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'customer_id': customer.customer_id,
                'profile_data': json.loads(customer.profile_data) if customer.profile_data else {}
            }
        
        # Get conversation history
        conversation = session.query(Message).filter(
            Message.customer_id == message.customer_id
        ).order_by(Message.created_at.asc()).all()
        
        conversation_data = []
        for msg in conversation:
            conversation_data.append({
                'id': msg.id,
                'content': msg.content,
                'direction': msg.direction,
                'agent_name': msg.agent_name,
                'created_at': msg.created_at.isoformat()
            })
        
        return jsonify({
            'message': {
                'id': message.id,
                'content': message.content,
                'status': message.status,
                'priority': message.priority,
                'created_at': message.created_at.isoformat()
            },
            'customer': customer_info,
            'conversation': conversation_data
        })
    finally:
        session.close()

@app.route('/api/messages/<int:message_id>/reply', methods=['POST'])
def reply_to_message(message_id):
    """Reply to a message"""
    session = Session()
    try:
        data = request.json
        content = data.get('content')
        agent_id = data.get('agent_id', 1)
        agent_name = data.get('agent_name', 'Agent')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        original_message = session.query(Message).filter(Message.id == message_id).first()
        if not original_message:
            return jsonify({'error': 'Message not found'}), 404
        
        # Create reply message
        reply = Message(
            customer_id=original_message.customer_id,
            content=content,
            direction='outgoing',
            agent_id=agent_id,
            agent_name=agent_name,
            status='sent'
        )
        session.add(reply)
        
        # Update original message status
        original_message.status = 'replied'
        original_message.replied_at = datetime.utcnow()
        
        session.commit()
        
        # Emit real-time update
        socketio.emit('new_reply', {
            'message_id': message_id,
            'reply': {
                'id': reply.id,
                'content': content,
                'agent_name': agent_name,
                'created_at': reply.created_at.isoformat()
            }
        })
        
        return jsonify({'success': True, 'reply_id': reply.id})
    finally:
        session.close()

@app.route('/api/customers/send-message', methods=['POST'])
def customer_send_message():
    """Endpoint for customers to send messages"""
    session = Session()
    try:
        data = request.json
        customer_name = data.get('name', 'Unknown Customer')
        customer_email = data.get('email', '')
        customer_phone = data.get('phone', '')
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Message content is required'}), 400
        
        # Find or create customer
        customer = session.query(Customer).filter(Customer.email == customer_email).first()
        if not customer:
            customer = Customer(
                name=customer_name,
                email=customer_email,
                phone=customer_phone,
                customer_id=f"CUST_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            )
            session.add(customer)
            session.flush()
        
        # Create message
        priority = calculate_priority(content)
        message = Message(
            customer_id=customer.id,
            content=content,
            direction='incoming',
            status='unread',
            priority=priority
        )
        session.add(message)
        session.commit()
        
        # Emit real-time update to agents
        socketio.emit('new_message', {
            'id': message.id,
            'customer_name': customer.name,
            'customer_email': customer.email,
            'content': content,
            'priority': priority,
            'created_at': message.created_at.isoformat()
        })
        
        return jsonify({'success': True, 'message_id': message.id})
    finally:
        session.close()

@app.route('/api/messages/<int:message_id>/read', methods=['POST'])
def mark_as_read(message_id):
    """Mark a message as read"""
    session = Session()
    try:
        message = session.query(Message).filter(Message.id == message_id).first()
        if message and message.status == 'unread':
            message.status = 'read'
            session.commit()
        return jsonify({'success': True})
    finally:
        session.close()

@app.route('/api/canned-messages', methods=['GET'])
def get_canned_messages():
    """Get all canned messages"""
    session = Session()
    try:
        messages = session.query(CannedMessage).all()
        result = [{
            'id': msg.id,
            'title': msg.title,
            'content': msg.content,
            'category': msg.category
        } for msg in messages]
        return jsonify(result)
    finally:
        session.close()

@app.route('/api/canned-messages', methods=['POST'])
def create_canned_message():
    """Create a new canned message"""
    session = Session()
    try:
        data = request.json
        canned = CannedMessage(
            title=data.get('title'),
            content=data.get('content'),
            category=data.get('category', 'general')
        )
        session.add(canned)
        session.commit()
        return jsonify({'success': True, 'id': canned.id})
    finally:
        session.close()

@app.route('/api/search', methods=['GET'])
def search():
    """Search messages and customers"""
    session = Session()
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'messages': [], 'customers': []})
        
        # Search messages
        messages = session.query(Message).join(Customer).filter(
            (Message.content.contains(query)) |
            (Customer.name.contains(query)) |
            (Customer.email.contains(query))
        ).limit(50).all()
        
        # Search customers
        customers = session.query(Customer).filter(
            (Customer.name.contains(query)) |
            (Customer.email.contains(query)) |
            (Customer.phone.contains(query))
        ).limit(20).all()
        
        return jsonify({
            'messages': [{
                'id': msg.id,
                'content': msg.content[:100],
                'customer_name': msg.customer.name if msg.customer else 'Unknown',
                'created_at': msg.created_at.isoformat()
            } for msg in messages],
            'customers': [{
                'id': cust.id,
                'name': cust.name,
                'email': cust.email,
                'phone': cust.phone
            } for cust in customers]
        })
    finally:
        session.close()

# Serve HTML files
@app.route('/')
def index():
    return send_from_directory('.', 'agent_ui.html')

@app.route('/agent')
def agent_ui():
    return send_from_directory('.', 'agent_ui.html')

@app.route('/customer')
def customer_form():
    return send_from_directory('.', 'customer_form.html')

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)

