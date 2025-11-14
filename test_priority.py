#!/usr/bin/env python3
"""
Test script to demonstrate priority detection
"""

# Copy of the priority detection logic from app.py
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
    matched_keywords = []
    
    for keyword in URGENCY_KEYWORDS['high']:
        if keyword in content_lower:
            priority = max(priority, 3)
            matched_keywords.append(f"HIGH: '{keyword}'")
    
    for keyword in URGENCY_KEYWORDS['medium']:
        if keyword in content_lower:
            priority = max(priority, 2)
            if priority < 3:  # Only add if not already high priority
                matched_keywords.append(f"MEDIUM: '{keyword}'")
    
    for keyword in URGENCY_KEYWORDS['low']:
        if keyword in content_lower:
            priority = max(priority, 1)
            if priority < 2:  # Only add if not already higher priority
                matched_keywords.append(f"LOW: '{keyword}'")
    
    return priority, matched_keywords

# Test cases
test_messages = [
    "When will my loan be disbursed? I need it urgently!",
    "What's the status of my loan approval?",
    "How to update my account information?",
    "I need to know about the approval process for my loan application.",
    "This is an emergency! I need help immediately!",
    "Can you tell me when I'll receive my funds?",
    "How do I change my email address?",
    "I'm asking about the timeline for disbursement.",
    "Just a general question about your services.",
    "URGENT: My loan disbursement is delayed!",
]

print("=" * 80)
print("PRIORITY DETECTION TEST")
print("=" * 80)
print()

priority_labels = {
    0: "None (Default)",
    1: "Low",
    2: "Medium", 
    3: "High/Urgent"
}

for i, message in enumerate(test_messages, 1):
    priority, keywords = calculate_priority(message)
    print(f"Test {i}:")
    print(f"  Message: \"{message}\"")
    print(f"  Priority: {priority} ({priority_labels[priority]})")
    if keywords:
        print(f"  Matched Keywords: {', '.join(keywords)}")
    else:
        print(f"  Matched Keywords: None")
    print()

print("=" * 80)
print("KEYWORD LISTS:")
print("=" * 80)
print(f"\nHigh Priority Keywords (Priority 3):")
print(f"  {', '.join(URGENCY_KEYWORDS['high'])}")
print(f"\nMedium Priority Keywords (Priority 2):")
print(f"  {', '.join(URGENCY_KEYWORDS['medium'])}")
print(f"\nLow Priority Keywords (Priority 1):")
print(f"  {', '.join(URGENCY_KEYWORDS['low'])}")
print()

