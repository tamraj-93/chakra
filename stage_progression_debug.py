#!/usr/bin/env python3
"""
Stage Progression Debugger

This script analyzes stage progression in template consultations by monitoring 
and instrumenting the backend to understand how and when stages advance.

Usage:
    python stage_progression_debug.py

Requirements:
    - Administrative access to the backend server
    - Backend service running
"""

import os
import sys
import json
import time
import requests
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stage_progression_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('stage_debugger')

# Configuration
CONFIG = {
    'api_base_url': 'http://localhost:8000/api',
    'username': 'admin',  # Admin user for API access
    'password': 'admin',  # Admin password
    'template_id': 'infrastructure-sla-template',  # Template to test
    'debug_logs_enabled': True,
    'save_results': True,
    'results_file': 'stage_progression_debug_results.json',
    'monitor_database': True,  # Set to True to monitor DB changes
    'enable_tracing': True,  # Set to True for detailed function call tracing
}

# Test messages for each stage
TEST_MESSAGES = [
    # Stage 1: Service Definition
    [
        "I need an SLA for my servers.",  # Basic - should not progress
        "We need SLAs for our mission-critical database servers and business-critical application servers.",  # Partial - should not progress
        "We need SLAs for our mission-critical database servers, business-critical application servers, and network infrastructure with varying criticality levels. These will be used by our IT operations team, finance department, and executive stakeholders. We need to ensure compliance with SOC 2 Type II, GDPR, HIPAA, and PCI DSS requirements."  # Complete - should progress
    ],
    # Stage 2: Availability Targets
    [
        "We need 99.9% uptime.",  # Minimal - should not progress
        "For mission-critical database servers, we need 99.999% availability with maximum downtime of 5.26 minutes per year.",  # Partial - should not progress
        "For mission-critical database servers, we need 99.999% availability with maximum downtime of 5.26 minutes per year and real-time monitoring. Business-critical application servers should have 99.99% availability with maximum 52.6 minutes downtime per year. For network infrastructure, we need varying levels: 99.999% for mission-critical segments and 99.99% for business-critical segments, with monitoring every minute."  # Complete - should progress
    ],
    # Stage 3: Performance Metrics
    [
        "We need fast database response times.",  # Basic - should not progress
        "For our database servers, we need response time under 100ms for queries and 1000 transactions per second minimum.",  # Partial - should not progress
        "For our database servers, we need response time under 100ms for queries, 1000 transactions per second minimum, and 99.9% query success rate. For application servers, we need page load times under 2 seconds, API response under 300ms, and support for at least 500 concurrent users. For network infrastructure, we need latency under 50ms, packet loss under 0.1%, and jitter under 30ms."  # Complete - should progress
    ],
    # Stage 4: Incident Response
    [
        "We need quick response times.",  # Basic - should not progress
        "For P1 critical incidents, we need 15-minute response time and 4-hour resolution.",  # Partial - should not progress
        "For P1 critical incidents, we need 15-minute response time and 4-hour resolution. For P2 incidents, 30-minute response and 8-hour resolution. P3 incidents should have 2-hour response and 24-hour resolution. We'll need monthly service credits of 10% for missing P1 SLAs, 5% for P2, and 2% for P3."  # Complete - should complete
    ]
]


class StageProgressionDebugger:
    """Debug tool for analyzing template stage progression."""

    def __init__(self, config=None):
        """Initialize the debugger with configuration."""
        self.config = config or CONFIG
        self.token = None
        self.session_id = None
        self.current_stage = 1
        self.progress = 0
        self.results = {
            'start_time': datetime.now().isoformat(),
            'session_id': None,
            'stages': [],
            'logs': [],
            'errors': []
        }

    def log(self, message: str, level: str = 'info') -> None:
        """Log a message and store it in results."""
        if level == 'info':
            logger.info(message)
        elif level == 'error':
            logger.error(message)
        elif level == 'debug':
            logger.debug(message)
        
        self.results['logs'].append({
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        })

    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """Log an error message."""
        if error:
            logger.error(f"{message}: {str(error)}")
            self.results['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'error': str(error)
            })
        else:
            logger.error(message)
            self.results['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'message': message
            })

    def authenticate(self) -> bool:
        """Authenticate with the API."""
        try:
            response = requests.post(
                f"{self.config['api_base_url']}/auth/login",
                json={'username': self.config['username'], 'password': self.config['password']}
            )
            response.raise_for_status()
            data = response.json()
            self.token = data.get('access_token')
            if not self.token:
                self.log_error("Authentication failed: No token received")
                return False
                
            self.log("Authentication successful")
            return True
        except Exception as e:
            self.log_error("Authentication failed", e)
            return False

    def start_session(self) -> bool:
        """Start a new template consultation session."""
        try:
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.post(
                f"{self.config['api_base_url']}/consultation/chat?template_id={self.config['template_id']}",
                headers=headers,
                json={'content': 'Start template consultation', 'role': 'user'}
            )
            response.raise_for_status()
            data = response.json()
            
            self.session_id = data.get('session_id')
            if not self.session_id:
                self.log_error("Failed to get session ID")
                return False
                
            self.results['session_id'] = self.session_id
            
            # Extract template progress
            template_progress = data.get('template_progress', {})
            self.current_stage = template_progress.get('current_stage', 1)
            self.progress = template_progress.get('progress_percentage', 0)
            
            self.log(f"Started session {self.session_id} at stage {self.current_stage} ({self.progress}%)")
            return True
        except Exception as e:
            self.log_error("Failed to start session", e)
            return False

    def send_message(self, message: str) -> Tuple[bool, Dict]:
        """Send a message to the consultation and return response with progression status."""
        try:
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.post(
                f"{self.config['api_base_url']}/consultation/chat?session_id={self.session_id}",
                headers=headers,
                json={'content': message, 'role': 'user'}
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract template progress
            template_progress = data.get('template_progress', {})
            new_stage = template_progress.get('current_stage', self.current_stage)
            new_progress = template_progress.get('progress_percentage', self.progress)
            
            # Check if stage progressed
            stage_progressed = new_stage > self.current_stage
            
            # Update stage info
            self.current_stage = new_stage
            self.progress = new_progress
            
            return stage_progressed, data
        except Exception as e:
            self.log_error(f"Failed to send message: {message}", e)
            return False, {}

    def force_next_stage(self) -> Tuple[bool, Dict]:
        """Force progression to the next stage."""
        try:
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.post(
                f"{self.config['api_base_url']}/consultation/sessions/{self.session_id}/force-next-stage",
                headers=headers,
                json={}
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract new stage information
            new_stage = data.get('current_stage_index', self.current_stage)
            new_progress = data.get('progress_percentage', self.progress)
            
            # Check if stage progressed
            stage_progressed = new_stage > self.current_stage
            
            # Update stage info
            self.current_stage = new_stage
            self.progress = new_progress
            
            self.log(f"Forced progression to stage {self.current_stage} ({self.progress}%)")
            
            return stage_progressed, data
        except Exception as e:
            self.log_error("Failed to force next stage", e)
            return False, {}

    def get_progress(self) -> Dict:
        """Get current session progress."""
        try:
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.get(
                f"{self.config['api_base_url']}/consultation/sessions/{self.session_id}/progress",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log_error("Failed to get progress", e)
            return {}

    def get_session_messages(self) -> List:
        """Get all messages in the session."""
        try:
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.get(
                f"{self.config['api_base_url']}/consultation/sessions/{self.session_id}/messages",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log_error("Failed to get session messages", e)
            return []

    def get_db_session_state(self) -> Dict:
        """Get the raw session state from database (admin only)."""
        if not self.config.get('monitor_database', False):
            return {}
            
        try:
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.get(
                f"{self.config['api_base_url']}/admin/sessions/{self.session_id}/state",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log_error("Failed to get DB session state", e)
            return {}

    def trace_ai_service_call(self, call_id: str) -> Dict:
        """Get trace information for an AI service call (requires tracing enabled)."""
        if not self.config.get('enable_tracing', False):
            return {}
            
        try:
            headers = {'Authorization': f"Bearer {self.token}"}
            response = requests.get(
                f"{self.config['api_base_url']}/admin/trace/{call_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log_error(f"Failed to get trace for call {call_id}", e)
            return {}

    def run_test_stage(self, stage_index: int, messages: List[str]) -> None:
        """Run tests for a specific stage."""
        self.log(f"\n===== TESTING STAGE {stage_index+1} =====")
        
        # Skip stages we've already completed
        if stage_index+1 < self.current_stage:
            self.log(f"Skipping stage {stage_index+1} (already completed)")
            return
            
        # If we're ahead of where we should be, something's wrong
        if stage_index+1 > self.current_stage:
            self.log_error(f"Error: Current stage ({self.current_stage}) doesn't match expected stage ({stage_index+1})")
            return
            
        stage_results = {
            'stage_number': stage_index + 1,
            'start_time': datetime.now().isoformat(),
            'tests': []
        }
            
        # Test each message for this stage
        for i, message in enumerate(messages):
            # Determine if this should cause progression (last message should)
            expect_progression = (i == len(messages) - 1)
            
            self.log(f"\nTest {i+1}/{len(messages)}: {'Complete' if expect_progression else 'Partial'} information")
            self.log(f"Message: {message[:50]}...")
            
            # Save state before test
            stage_before = self.current_stage
            progress_before = self.progress
            
            # Send the message
            progressed, response = self.send_message(message)
            
            # Create test result
            test_result = {
                'message': message,
                'expected_progression': expect_progression,
                'actual_progression': progressed,
                'progress_before': progress_before,
                'progress_after': self.progress,
                'result': 'success' if progressed == expect_progression else 'failure'
            }
            
            # Enrich with tracing data if enabled
            if self.config.get('enable_tracing', False) and 'trace_id' in response:
                trace_data = self.trace_ai_service_call(response['trace_id'])
                test_result['trace_data'] = trace_data
                
            # Add to results
            stage_results['tests'].append(test_result)
            
            # Log the result
            self.log(f"Stage progressed: {'YES' if progressed else 'NO'}")
            self.log(f"Progress: {progress_before}% → {self.progress}%")
            self.log(f"Expected progression: {'YES' if expect_progression else 'NO'}")
            self.log(f"Result: {'SUCCESS' if progressed == expect_progression else 'FAILURE'}")
            
            # Get session state for debugging
            if self.config.get('monitor_database', False):
                db_state = self.get_db_session_state()
                test_result['db_state'] = db_state
                
                # Debug state information
                self.log(f"Session state: {json.dumps(db_state.get('session_state', {}), indent=2)}")
                
            # If we've already progressed, we're done with this stage
            if progressed:
                self.log(f"Successfully progressed to stage {self.current_stage}")
                break
                
        # Finalize stage results
        stage_results['end_time'] = datetime.now().isoformat()
        stage_results['final_stage'] = self.current_stage
        stage_results['final_progress'] = self.progress
        
        # Add to overall results
        self.results['stages'].append(stage_results)

    def run_all_tests(self) -> None:
        """Run tests for all stages."""
        self.log("\nStarting stage progression tests")
        
        for stage_index, messages in enumerate(TEST_MESSAGES):
            self.run_test_stage(stage_index, messages)
            
        self.log("\n===== TEST SUMMARY =====")
        success_count = sum(1 for stage in self.results['stages'] for test in stage['tests'] if test['result'] == 'success')
        failure_count = sum(1 for stage in self.results['stages'] for test in stage['tests'] if test['result'] == 'failure')
        
        self.log(f"Tests run: {success_count + failure_count}")
        self.log(f"Success: {success_count}")
        self.log(f"Failures: {failure_count}")
        
        self.results['end_time'] = datetime.now().isoformat()
        
        # Save results
        if self.config.get('save_results', True):
            self.save_results()

    def save_results(self) -> None:
        """Save test results to file."""
        try:
            with open(self.config.get('results_file', 'stage_progression_debug_results.json'), 'w') as f:
                json.dump(self.results, f, indent=2)
            self.log(f"Results saved to {self.config.get('results_file')}")
        except Exception as e:
            self.log_error("Failed to save results", e)
            
    def analyze_stages(self) -> Dict:
        """Analyze stage progression pattern and provide insights."""
        analysis = {
            'stage_insights': [],
            'common_issues': [],
            'recommendations': []
        }
        
        if not self.results['stages']:
            return analysis
        
        # Analyze each stage
        for stage in self.results['stages']:
            stage_analysis = {
                'stage': stage['stage_number'],
                'progression_success': False,
                'insights': []
            }
            
            # Check if any test succeeded in progression
            successful_progression = any(test['actual_progression'] for test in stage['tests'])
            stage_analysis['progression_success'] = successful_progression
            
            # Add stage-specific insights
            if not successful_progression:
                stage_analysis['insights'].append("No test succeeded in advancing this stage")
            
            # Check pattern of success/failure
            for test in stage['tests']:
                if test['expected_progression'] and not test['actual_progression']:
                    stage_analysis['insights'].append(
                        "Complete information didn't trigger progression - possible issue with completeness detection"
                    )
                elif not test['expected_progression'] and test['actual_progression']:
                    stage_analysis['insights'].append(
                        "Incomplete information triggered progression - possible issue with progression threshold"
                    )
            
            analysis['stage_insights'].append(stage_analysis)
        
        # Generate common issues
        progression_failures = [
            stage for stage in analysis['stage_insights'] 
            if not stage['progression_success']
        ]
        
        if progression_failures:
            analysis['common_issues'].append(
                f"Failed to progress automatically in {len(progression_failures)} stages"
            )
        
        # Generate recommendations
        if progression_failures:
            analysis['recommendations'].append(
                "Review the stage progression logic in ai.py to ensure it correctly identifies complete responses"
            )
            analysis['recommendations'].append(
                "Consider adjusting the stage completion threshold in the AI service"
            )
            analysis['recommendations'].append(
                "Examine how session_state is updated after each message"
            )
        
        return analysis


def main():
    """Run the stage progression debugger."""
    debugger = StageProgressionDebugger()
    
    # Authentication
    if not debugger.authenticate():
        logger.error("Authentication failed. Exiting.")
        return
        
    # Start session
    if not debugger.start_session():
        logger.error("Failed to start session. Exiting.")
        return
        
    # Run tests
    debugger.run_all_tests()
    
    # Analyze results
    analysis = debugger.analyze_stages()
    logger.info("\n===== ANALYSIS =====")
    
    for section, items in analysis.items():
        logger.info(f"\n{section.upper()}:")
        for item in items:
            if isinstance(item, dict):
                logger.info(f"- Stage {item['stage']}: {'Success' if item['progression_success'] else 'Failure'}")
                for insight in item['insights']:
                    logger.info(f"  • {insight}")
            else:
                logger.info(f"- {item}")


if __name__ == "__main__":
    main()