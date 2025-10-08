"""
Healthcare document classification service for the Knowledge Base.
Provides functions to analyze and classify SLA documents related to healthcare.
"""

import re
from typing import Dict, List, Any, Optional, Tuple

# Healthcare terminology dictionaries for classification
HEALTHCARE_TERMS = {
    "clinical": [
        "clinical workflow", "treatment", "diagnosis", "patient care", "medical history",
        "prognosis", "prescription", "medication", "laboratory", "vital signs",
        "patient record", "consultation", "medical exam", "physician", "nurse",
        "clinician", "specialist", "referral", "triage", "medical imaging"
    ],
    "administrative": [
        "billing", "coding", "insurance", "claims", "reimbursement",
        "scheduling", "appointment", "registration", "intake", "discharge",
        "revenue cycle", "preauthorization", "eligibility", "benefits", "copay",
        "deductible", "coordination of benefits", "credentialing", "provider network"
    ],
    "technical": [
        "interoperability", "HL7", "FHIR", "API", "database",
        "server", "bandwidth", "latency", "throughput", "uptime",
        "backup", "disaster recovery", "failover", "load balancing", "high availability",
        "virtualization", "cloud hosting", "authentication", "encryption", "firewall"
    ],
    "regulatory": [
        "HIPAA", "HITECH", "compliance", "audit", "OCR",
        "privacy", "security rule", "breach notification", "business associate", "covered entity",
        "minimum necessary", "safe harbor", "consent", "authorization", "accounting of disclosures",
        "data protection officer", "privacy officer", "security officer", "documentation", "policies and procedures"
    ],
    "data": [
        "PHI", "ePHI", "protected health information", "personally identifiable information", "PII",
        "medical record", "health record", "clinical data", "patient data", "health information",
        "structured data", "unstructured data", "metadata", "data element", "data dictionary",
        "data model", "data warehouse", "data lake", "data governance", "data quality"
    ]
}

COMPLIANCE_FRAMEWORKS = {
    "HIPAA": [
        "HIPAA", "Health Insurance Portability and Accountability Act", "Privacy Rule", "Security Rule",
        "PHI", "ePHI", "covered entity", "business associate", "breach notification"
    ],
    "HITECH": [
        "HITECH", "Health Information Technology for Economic and Clinical Health",
        "meaningful use", "electronic health record incentive program"
    ],
    "42 CFR Part 2": [
        "42 CFR Part 2", "substance use disorder", "Part 2", "drug abuse", "alcohol abuse",
        "substance abuse", "addiction treatment", "substance use record"
    ],
    "HITRUST": [
        "HITRUST", "CSF", "Common Security Framework", "HITRUST certification", 
        "HITRUST assessment", "HITRUST validation", "HITRUST scorecard"
    ],
    "GDPR for Health": [
        "GDPR", "General Data Protection Regulation", "data subject", "controller", "processor",
        "consent", "right to be forgotten", "data portability", "EU", "European"
    ],
    "Joint Commission": [
        "Joint Commission", "accreditation", "JCAHO", "sentinel event", "patient safety goals",
        "standards compliance", "tracer methodology", "survey", "continuous compliance"
    ]
}

class HealthcareDocumentClassifier:
    """Classifier for healthcare-specific documents"""
    
    def classify_document(self, content: str, filename: str) -> Dict[str, Any]:
        """
        Classify a healthcare document based on its content
        Returns a dictionary of healthcare-specific metadata
        """
        # Initialize classification results
        classification = {
            "is_healthcare": False,
            "industry": None,
            "service_type": None,
            "healthcare_category": None,
            "compliance_frameworks": [],
            "clinical_specialties": [],
            "data_sensitivity": None,
            "key_healthcare_terms": {},
            "confidence_score": 0.0
        }
        
        # Check if this is a healthcare document
        healthcare_score, category_scores = self._calculate_healthcare_score(content)
        
        if healthcare_score > 0.4:  # 40% confidence threshold
            classification["is_healthcare"] = True
            classification["confidence_score"] = healthcare_score
            classification["industry"] = "Healthcare - General"
            
            # Determine primary healthcare category based on term frequency
            primary_category = max(category_scores.items(), key=lambda x: x[1])
            classification["key_healthcare_terms"] = category_scores
            
            # Set healthcare category
            if primary_category[0] == "clinical" and primary_category[1] > 0.1:
                classification["healthcare_category"] = "Clinical Information Systems"
            elif primary_category[0] == "administrative" and primary_category[1] > 0.1:
                classification["healthcare_category"] = "Administrative Systems"
            elif primary_category[0] == "technical" and primary_category[1] > 0.1:
                classification["healthcare_category"] = "Healthcare IT Infrastructure"
            elif primary_category[0] == "data" and primary_category[1] > 0.1:
                classification["healthcare_category"] = "Health Data Management"
            
            # Detect service type
            classification["service_type"] = self._detect_service_type(content)
            
            # Detect compliance frameworks
            classification["compliance_frameworks"] = self._detect_compliance_frameworks(content)
            
            # Detect clinical specialties
            classification["clinical_specialties"] = self._detect_clinical_specialties(content)
            
            # Determine data sensitivity
            classification["data_sensitivity"] = self._determine_data_sensitivity(
                content, 
                classification["compliance_frameworks"]
            )
        
        return classification
    
    def _calculate_healthcare_score(self, content: str) -> Tuple[float, Dict[str, float]]:
        """Calculate how likely the document is related to healthcare"""
        # Normalize content for better matching
        normalized_content = content.lower()
        word_count = len(re.findall(r'\w+', normalized_content))
        
        if word_count == 0:
            return 0.0, {}
        
        # Count matches for each category
        category_scores = {}
        total_matches = 0
        
        for category, terms in HEALTHCARE_TERMS.items():
            category_count = 0
            for term in terms:
                matches = len(re.findall(r'\b' + re.escape(term.lower()) + r'\b', normalized_content))
                if matches > 0:
                    category_count += matches
            
            category_scores[category] = category_count / word_count
            total_matches += category_count
        
        # Calculate overall healthcare score
        healthcare_score = min(1.0, total_matches / (word_count * 0.05))  # Cap at 1.0
        
        return healthcare_score, category_scores
    
    def _detect_service_type(self, content: str) -> Optional[str]:
        """Detect the healthcare service type from the document content"""
        service_type_patterns = {
            "EHR Hosting": [
                r'\b(EHR|electronic health record|EMR|electronic medical record)\b.{0,30}\b(hosting|cloud|infrastructure|platform)\b',
                r'\b(hosting|cloud|infrastructure|platform).{0,30}\b(EHR|electronic health record|EMR|electronic medical record)\b'
            ],
            "Telemedicine Platform": [
                r'\b(telemedicine|telehealth|virtual care|video consult|remote care)\b',
                r'\bvirtual\s(visit|appointment|consultation)\b'
            ],
            "Patient Portal": [
                r'\b(patient portal|patient access|patient engagement)\b',
                r'\bpatient.{0,10}\bportal\b'
            ],
            "Health Information Exchange": [
                r'\b(HIE|health information exchange|health data exchange)\b',
                r'\bexchange.{0,20}(health|medical|clinical).{0,20}information\b'
            ],
            "Medical Imaging Storage": [
                r'\b(PACS|picture archiving|radiology storage|medical image|imaging repository)\b',
                r'\b(CT|MRI|ultrasound|X-ray|radiograph).{0,30}(storage|archive)\b'
            ]
        }
        
        normalized_content = content.lower()
        
        for service_type, patterns in service_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, normalized_content, re.IGNORECASE):
                    return service_type
        
        return None
    
    def _detect_compliance_frameworks(self, content: str) -> List[str]:
        """Detect regulatory compliance frameworks mentioned in the document"""
        frameworks = []
        normalized_content = content.lower()
        
        for framework, indicators in COMPLIANCE_FRAMEWORKS.items():
            for indicator in indicators:
                if re.search(r'\b' + re.escape(indicator.lower()) + r'\b', normalized_content):
                    if framework not in frameworks:
                        frameworks.append(framework)
                    break
        
        return frameworks
    
    def _detect_clinical_specialties(self, content: str) -> List[str]:
        """Detect clinical specialties mentioned in the document"""
        specialties = []
        specialty_list = [
            "Cardiology", "Radiology", "Pediatrics", "Oncology", 
            "Neurology", "Orthopedics", "Primary Care", "Emergency Medicine", 
            "Surgery", "Obstetrics", "Gynecology", "Psychiatry", "Dermatology",
            "Ophthalmology", "Endocrinology", "Gastroenterology", "Urology"
        ]
        
        for specialty in specialty_list:
            if re.search(r'\b' + re.escape(specialty) + r'\b', content, re.IGNORECASE):
                specialties.append(specialty)
        
        return specialties
    
    def _determine_data_sensitivity(self, content: str, compliance_frameworks: List[str]) -> str:
        """Determine the data sensitivity level based on content and compliance frameworks"""
        # Check for high sensitivity indicators
        high_sensitivity_patterns = [
            r'\bPHI\b', r'\bePHI\b', r'\bprotected health information\b',
            r'\bsensitive\s+patient\s+data\b', r'\bmedical\s+record\b',
            r'\bsubstance\s+(use|abuse)\b', r'\bmental\s+health\b', r'\bHIV\b',
            r'\bgenetic\b', r'\bbiometric\b'
        ]
        
        for pattern in high_sensitivity_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return "High"
        
        # Consider compliance frameworks
        if "HIPAA" in compliance_frameworks or "42 CFR Part 2" in compliance_frameworks:
            return "High"
        elif len(compliance_frameworks) > 0:
            return "Medium"
            
        # Default sensitivity
        return "Medium"