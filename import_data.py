import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Base, Customer, Message, CannedMessage, calculate_priority
import os
import json
from datetime import datetime

# Database setup
engine = create_engine('sqlite:///messaging_app.db', echo=False)
Session = sessionmaker(bind=engine)

def import_excel_files():
    """Import all Excel files from the current directory"""
    session = Session()
    try:
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and 'MessageData' in f]
        
        print(f"Found {len(excel_files)} Excel files to import")
        
        for excel_file in excel_files:
            print(f"\nProcessing {excel_file}...")
            try:
                df = pd.read_excel(excel_file)
                print(f"  Columns: {df.columns.tolist()}")
                print(f"  Rows: {len(df)}")
                
               
                name_col = None
                email_col = None
                phone_col = None
                message_col = None
                customer_id_col = None
                
                for col in df.columns:
                    col_lower = str(col).lower()
                    if 'name' in col_lower and name_col is None:
                        name_col = col
                    elif 'email' in col_lower and email_col is None:
                        email_col = col
                    elif 'phone' in col_lower or 'mobile' in col_lower:
                        phone_col = col
                    elif 'message' in col_lower or 'content' in col_lower or 'text' in col_lower:
                        message_col = col
                    elif 'customer' in col_lower and 'id' in col_lower:
                        customer_id_col = col
                
                # If we can't find message column, use the first text-like column
                if message_col is None:
                    for col in df.columns:
                        if df[col].dtype == 'object':
                            message_col = col
                            break
                
                print(f"  Using columns: name={name_col}, email={email_col}, phone={phone_col}, message={message_col}")
                
                imported = 0
                for idx, row in df.iterrows():
                    try:
                        # Get customer info
                        name = str(row[name_col]) if name_col and pd.notna(row.get(name_col)) else f"Customer {idx+1}"
                        email = str(row[email_col]) if email_col and pd.notna(row.get(email_col)) else f"customer{idx+1}@example.com"
                        phone = str(row[phone_col]) if phone_col and pd.notna(row.get(phone_col)) else ""
                        message_content = str(row[message_col]) if message_col and pd.notna(row.get(message_col)) else ""
                        customer_id_val = str(row[customer_id_col]) if customer_id_col and pd.notna(row.get(customer_id_col)) else None
                        
                        if not message_content or message_content == 'nan':
                            continue
                        
                        # Find or create customer
                        customer = None
                        if customer_id_val:
                            customer = session.query(Customer).filter(Customer.customer_id == customer_id_val).first()
                        
                        if not customer and email:
                            customer = session.query(Customer).filter(Customer.email == email).first()
                        
                        if not customer:
                            customer = Customer(
                                name=name,
                                email=email,
                                phone=phone,
                                customer_id=customer_id_val or f"CUST_IMPORT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{idx}"
                            )
                            # Add some mock profile data
                            customer.profile_data = json.dumps({
                                'account_type': 'premium' if idx % 3 == 0 else 'standard',
                                'join_date': (datetime.utcnow().replace(day=1) if idx % 2 == 0 else datetime.utcnow()).isoformat(),
                                'total_messages': 0,
                                'last_contact': None
                            })
                            session.add(customer)
                            session.flush()
                        
                        # Check if message already exists (avoid duplicates)
                        existing_message = session.query(Message).filter(
                            Message.customer_id == customer.id,
                            Message.content == message_content,
                            Message.direction == 'incoming'
                        ).first()
                        
                        if not existing_message:
                            # Create message
                            priority = calculate_priority(message_content)
                            message = Message(
                                customer_id=customer.id,
                                content=message_content,
                                direction='incoming',
                                status='unread',
                                priority=priority
                            )
                            session.add(message)
                            imported += 1
                        
                    except Exception as e:
                        print(f"    Error processing row {idx}: {e}")
                        continue
                
                session.commit()
                print(f"  Imported {imported} messages from {excel_file}")
                
            except Exception as e:
                print(f"  Error processing {excel_file}: {e}")
                session.rollback()
                continue
        
        print(f"\nImport completed!")
        
    finally:
        session.close()

def create_default_canned_messages():
    """Create some default canned messages"""
    session = Session()
    try:
        canned_messages = [
            {
                'title': 'Loan Approval Status',
                'content': 'Thank you for contacting us. We are currently reviewing your loan application. You will receive an update within 2-3 business days. If you have any urgent concerns, please let us know.',
                'category': 'loan'
            },
            {
                'title': 'Loan Disbursement Timeline',
                'content': 'Once your loan is approved, disbursement typically occurs within 1-2 business days. You will receive a notification once the funds have been transferred to your account.',
                'category': 'loan'
            },
            {
                'title': 'Update Account Information',
                'content': 'To update your account information, please log in to your Branch account and navigate to Settings > Profile. If you need assistance, we can help guide you through the process.',
                'category': 'account'
            },
            {
                'title': 'General Inquiry',
                'content': 'Thank you for reaching out. We have received your message and will respond to your inquiry shortly. If this is urgent, please call our support line.',
                'category': 'general'
            },
            {
                'title': 'Password Reset',
                'content': 'To reset your password, please click on "Forgot Password" on the login page and follow the instructions sent to your registered email address.',
                'category': 'account'
            }
        ]
        
        for msg_data in canned_messages:
            existing = session.query(CannedMessage).filter(
                CannedMessage.title == msg_data['title']
            ).first()
            if not existing:
                canned = CannedMessage(**msg_data)
                session.add(canned)
        
        session.commit()
        print("Created default canned messages")
    finally:
        session.close()

if __name__ == '__main__':
    print("Starting data import...")
    import_excel_files()
    print("\nCreating default canned messages...")
    create_default_canned_messages()
    print("\nDone!")

