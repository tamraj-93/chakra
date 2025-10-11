"""
Demo Mode Module for Chakra Application
Comprehensive Fallback Demo Mode for Chakra

This module provides mock implementations of AI capabilities
for demonstration purposes when running in demo mode.
"""

import os
import json
import random
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample responses for different query types
GREETING_RESPONSES = [
    "Hello! I'm Chakra AI assistant running in demo mode. I can help analyze SLAs and provide recommendations.",
    "Hi there! This is Chakra in demo mode. I can demonstrate how AI would analyze your SLAs.",
    "Welcome to Chakra! I'm currently running in demo mode with pre-defined responses.",
]

SLA_ANALYSIS_RESPONSES = [
    """
    ## SLA Analysis Summary
    
    Based on my review of this SLA document, here are the key points:
    
    ### Service Level Targets
    - **Availability**: 99.95% uptime commitment
    - **Response Time**: Critical issues: 15 minutes, High: 2 hours, Medium: 8 hours
    - **Resolution Time**: Critical: 4 hours, High: 12 hours, Medium: 24 hours
    
    ### Areas of Concern
    - The penalty structure is weighted in favor of the provider
    - No specific compensation for repeated failures
    - Ambiguous definition of "downtime" could lead to disputes
    
    ### Recommendations
    1. Request clearer definition of service measurement methodology
    2. Strengthen the penalty clauses for repeated violations
    3. Include a detailed escalation procedure for unresolved issues
    """,
    
    """
    ## SLA Document Review
    
    After analyzing this SLA, I've identified the following:
    
    ### Key Metrics
    - **System Uptime**: 99.9% monthly commitment
    - **Incident Response**: P1: 30min, P2: 2hrs, P3: 8hrs
    - **Support Hours**: 24/7 for critical issues, 9am-5pm for others
    
    ### Potential Risks
    - Broad force majeure clauses that could exempt provider from responsibility
    - Limited remedies for service failures (credits only)
    - No commitment to recovery point objectives (RPO)
    
    ### Suggested Improvements
    1. Add specific recovery time objectives for different failure scenarios
    2. Include reporting requirements with regular SLA performance reviews
    3. Strengthen service credits to better reflect business impact
    """,
]

RECOMMENDATIONS_BY_INDUSTRY = {
    "healthcare": [
        """
        ## Healthcare SLA Recommendations
        
        For healthcare organizations, I recommend the following SLA provisions:
        
        ### Critical Components
        - **HIPAA/HITECH Compliance**: Explicit guarantee of regulatory compliance
        - **Data Breach Response**: 1-hour notification and detailed response plan
        - **Backup Requirements**: 15-minute RPO, 1-hour RTO for critical systems
        - **Uptime**: 99.99% for clinical systems, 99.9% for administrative
        
        ### Specific Clauses to Include
        1. PHI handling procedures with audit requirements
        2. Business Associate Agreement integration
        3. Regular security assessment schedule
        4. Clear data sanitization procedures upon contract termination
        """,
        
        """
        ## Healthcare Industry SLA Guidelines
        
        For your healthcare SLA, consider these essential elements:
        
        ### Key Metrics
        - **System Availability**: 99.99% for patient-facing systems
        - **Data Security**: SOC 2 Type II compliance
        - **Disaster Recovery**: 15-minute RPO, 1-hour RTO
        
        ### Regulatory Requirements
        1. HIPAA compliance attestation
        2. Annual penetration testing
        3. Patient data segregation guarantees
        
        ### Support Structure
        - 24/7 clinical support with max 15-minute response
        - Dedicated technical account manager
        - Monthly compliance reporting
        """
    ],
    
    "finance": [
        """
        ## Financial Services SLA Guidelines
        
        For financial institutions, your SLA should include:
        
        ### Security & Compliance
        - **Data Encryption**: AES-256 for data at rest and in transit
        - **Authentication**: Multi-factor authentication requirements
        - **Regulatory Reporting**: Automated compliance reporting
        
        ### Performance Metrics
        - **Transaction Processing**: 99.999% uptime, <500ms response time
        - **Batch Processing**: Guaranteed completion windows
        - **Failover**: Automatic failover under 5 minutes
        
        ### Risk Mitigation
        1. Explicit PCI-DSS compliance requirements
        2. Financial liability caps aligned with potential losses
        3. Continuous monitoring with real-time alerting
        """,
        
        """
        ## Banking & Finance SLA Recommendations
        
        Your financial services SLA should prioritize:
        
        ### Essential Guarantees
        - **System Availability**: 99.999% for transaction systems
        - **Security Compliance**: SOC 1, SOC 2, PCI-DSS certification
        - **Disaster Recovery**: Geographically separate data centers with real-time replication
        
        ### Legal Protections
        1. Limited liability clauses appropriate to transaction volumes
        2. Clear definition of security incident procedures
        3. Data ownership and return guarantees
        
        ### Performance Requirements
        - Transaction response times under 300ms
        - API availability 99.99%
        - 24/7/365 support with 15-minute response for critical issues
        """
    ],
    
    "technology": [
        """
        ## Technology Sector SLA Best Practices
        
        For SaaS and technology providers, focus on:
        
        ### Technical Guarantees
        - **API Performance**: Response times <100ms, 99.9% availability
        - **Scalability**: Clear resource allocation with burst capacity
        - **Integration Support**: SLA coverage for third-party connections
        
        ### Service Metrics
        - **Feature Availability**: Per-feature uptime guarantees
        - **Support Tiers**: Standard vs. Premium with response time differentiation
        - **Maintenance Windows**: Limited, scheduled, with advance notice
        
        ### Modern Provisions
        1. Service degradation metrics (not just outages)
        2. Platform-specific performance guarantees
        3. Transparent incident communication requirements
        """,
        
        """
        ## SaaS & Technology SLA Components
        
        Your technology SLA should include these modern elements:
        
        ### Performance Metrics
        - **Application Response Time**: 95th percentile under 500ms
        - **API Availability**: 99.95% with rate limiting policies
        - **Background Job Processing**: Guaranteed processing times
        
        ### DevOps Integration
        1. Deployment frequency limitations
        2. Rollback commitments
        3. Feature flag coordination
        
        ### Modern Support Structure
        - Chat support response in 5 minutes
        - Self-service status page with component-level detail
        - Retrospective requirements after incidents
        """
    ]
}

GENERAL_RECOMMENDATIONS = [
    """
    ## General SLA Improvement Recommendations
    
    To strengthen any SLA document, consider these best practices:
    
    ### Essential Components
    - **Clear Metrics**: Define exactly how each metric is measured
    - **Meaningful Remedies**: Ensure credits reflect business impact
    - **Reporting**: Require regular, detailed performance reports
    
    ### Legal Protections
    1. Limitation of liability appropriate to service importance
    2. Clear definition of security incident procedures
    3. Termination rights for repeated SLA failures
    
    ### Operational Elements
    - Clear escalation procedures with named roles
    - Change management processes
    - Regular service review meetings
    """,
    
    """
    ## SLA Best Practices
    
    Here are key elements every strong SLA should include:
    
    ### Measurement & Reporting
    - **Precise Calculations**: Exact formulas for all metrics
    - **Exclusions**: Clear definition of excluded events
    - **Transparency**: Customer access to monitoring data
    
    ### Service Credits
    1. Automatic application without requiring claims
    2. Graduated structure based on severity
    3. Look-back periods for repeated failures
    
    ### Governance
    - Regular service review meetings
    - Continuous improvement mechanisms
    - Clear amendment processes
    """
]

class MockLLMProvider:
    """Mock implementation of an LLM provider for demo mode"""
    
    def __init__(self):
        """Initialize the mock LLM provider"""
        logger.info("Initializing Mock LLM Provider for demo mode")
        self.conversation_history = []
    
    def chat_completion(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Generate a mock chat completion response
        
        Args:
            messages: List of message objects with role and content
            **kwargs: Additional parameters (ignored in demo mode)
            
        Returns:
            Dict containing the response
        """
        # Store messages in conversation history
        self.conversation_history.extend(messages)
        
        # Get the last user message
        last_message = messages[-1]["content"] if messages else ""
        
        # Generate appropriate response based on message content
        if self._is_greeting(last_message):
            content = random.choice(GREETING_RESPONSES)
        elif self._is_about_sla_analysis(last_message):
            content = random.choice(SLA_ANALYSIS_RESPONSES)
        elif "healthcare" in last_message.lower():
            content = random.choice(RECOMMENDATIONS_BY_INDUSTRY["healthcare"])
        elif any(term in last_message.lower() for term in ["finance", "banking", "financial"]):
            content = random.choice(RECOMMENDATIONS_BY_INDUSTRY["finance"])
        elif any(term in last_message.lower() for term in ["technology", "tech", "software", "saas"]):
            content = random.choice(RECOMMENDATIONS_BY_INDUSTRY["technology"])
        else:
            content = random.choice(GENERAL_RECOMMENDATIONS)
        
        # Return formatted response
        return {
            "id": f"chatcmpl-demo-{random.randint(1000, 9999)}",
            "object": "chat.completion",
            "created": 1677858242,
            "model": "gpt-3.5-turbo-demo",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "index": 0,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(last_message) // 4,
                "completion_tokens": len(content) // 4,
                "total_tokens": (len(last_message) + len(content)) // 4
            }
        }
    
    def _is_greeting(self, text: str) -> bool:
        """Check if text is a greeting"""
        greeting_terms = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"]
        text = text.lower()
        return any(term in text for term in greeting_terms) and len(text) < 20
    
    def _is_about_sla_analysis(self, text: str) -> bool:
        """Check if text is requesting SLA analysis"""
        sla_terms = ["analyze", "analysis", "review", "check", "evaluate"]
        text = text.lower()
        return "sla" in text and any(term in text for term in sla_terms)

def get_mock_provider():
    """Get a mock LLM provider instance for demo mode"""
    return MockLLMProvider()

def is_demo_mode() -> bool:
    """Check if application is running in demo mode"""
    return os.environ.get("DEMO_MODE", "").lower() == "true"
