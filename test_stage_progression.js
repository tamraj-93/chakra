/**
 * Stage Progression Testing Script
 * 
 * This script helps debug and track issues with stage progression in template consultations.
 * It provides a systematic way to test and understand when stages properly advance and when they don't.
 */

// Configuration
const TEST_CONFIG = {
  apiBaseUrl: 'http://localhost:8000/api',
  frontendUrl: 'http://localhost:4200',
  templateId: 'infrastructure-sla-template', // Update with your actual template ID
  debugLogsEnabled: true,
  saveResults: true,
  resultsFilePath: './stage_progression_results.json'
};

// Test cases for each stage of the SLA template
const TEST_CASES = [
  {
    stage: 1,
    stageName: 'Service Definition',
    description: 'Define the infrastructure services requiring SLAs',
    testInputs: [
      {
        label: 'Basic input - should not progress',
        message: 'I need an SLA for my servers.',
        expectProgression: false
      },
      {
        label: 'Partial information - should not progress',
        message: 'We need SLAs for our mission-critical database servers and business-critical application servers.',
        expectProgression: false
      },
      {
        label: 'Complete information - should progress',
        message: 'We need SLAs for our mission-critical database servers, business-critical application servers, and network infrastructure with varying criticality levels. These will be used by our IT operations team, finance department, and executive stakeholders. We need to ensure compliance with SOC 2 Type II, GDPR, HIPAA, and PCI DSS requirements.',
        expectProgression: true
      }
    ]
  },
  {
    stage: 2,
    stageName: 'Availability Targets',
    description: 'Define uptime requirements and monitoring frequency',
    testInputs: [
      {
        label: 'Minimal input - should not progress',
        message: 'We need 99.9% uptime.',
        expectProgression: false
      },
      {
        label: 'Partial information - should not progress',
        message: 'For mission-critical database servers, we need 99.999% availability with maximum downtime of 5.26 minutes per year.',
        expectProgression: false
      },
      {
        label: 'Complete information - should progress',
        message: 'For mission-critical database servers, we need 99.999% availability with maximum downtime of 5.26 minutes per year and real-time monitoring. Business-critical application servers should have 99.99% availability with maximum 52.6 minutes downtime per year. For network infrastructure, we need varying levels: 99.999% for mission-critical segments and 99.99% for business-critical segments, with monitoring every minute.',
        expectProgression: true
      }
    ]
  },
  {
    stage: 3,
    stageName: 'Performance Metrics',
    description: 'Define performance requirements for each service',
    testInputs: [
      {
        label: 'Basic input - should not progress',
        message: 'We need fast database response times.',
        expectProgression: false
      },
      {
        label: 'Partial information - should not progress',
        message: 'For our database servers, we need response time under 100ms for queries and 1000 transactions per second minimum.',
        expectProgression: false
      },
      {
        label: 'Complete information - should progress',
        message: 'For our database servers, we need response time under 100ms for queries, 1000 transactions per second minimum, and 99.9% query success rate. For application servers, we need page load times under 2 seconds, API response under 300ms, and support for at least 500 concurrent users. For network infrastructure, we need latency under 50ms, packet loss under 0.1%, and jitter under 30ms.',
        expectProgression: true
      }
    ]
  },
  {
    stage: 4,
    stageName: 'Incident Response',
    description: 'Define response times and resolution targets',
    testInputs: [
      {
        label: 'Basic input - should not progress',
        message: 'We need quick response times.',
        expectProgression: false
      },
      {
        label: 'Partial information - should not progress',
        message: 'For P1 critical incidents, we need 15-minute response time and 4-hour resolution.',
        expectProgression: false
      },
      {
        label: 'Complete information - should complete consultation',
        message: "For P1 critical incidents, we need 15-minute response time and 4-hour resolution. For P2 incidents, 30-minute response and 8-hour resolution. P3 incidents should have 2-hour response and 24-hour resolution. We'll need monthly service credits of 10% for missing P1 SLAs, 5% for P2, and 2% for P3.",
        expectProgression: true
      }
    ]
  }
];

// StageProgressionTester class
class StageProgressionTester {
  constructor(config = TEST_CONFIG, testCases = TEST_CASES) {
    this.config = config;
    this.testCases = testCases;
    this.currentSession = null;
    this.results = {
      startTime: new Date().toISOString(),
      sessionId: null,
      tests: []
    };
    this.debugLogs = [];
  }

  /**
   * Initialize testing session
   */
  async init() {
    this.log('Initializing stage progression test...');
    await this.startSession();
  }

  /**
   * Start a new template consultation session
   */
  async startSession() {
    try {
      const response = await fetch(`${this.config.apiBaseUrl}/consultation/chat?template_id=${this.config.templateId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        body: JSON.stringify({
          content: 'Start template consultation',
          role: 'user'
        })
      });

      const data = await response.json();
      this.currentSession = {
        sessionId: data.session_id,
        currentStage: data.template_progress.current_stage || 1,
        progress: data.template_progress.progress_percentage || 0
      };

      this.results.sessionId = this.currentSession.sessionId;
      this.log(`Session started with ID: ${this.currentSession.sessionId}`);
    } catch (error) {
      this.logError('Failed to start session:', error);
    }
  }

  /**
   * Run all test cases for all stages
   */
  async runAllTests() {
    if (!this.currentSession) {
      this.logError('No active session. Please initialize first.');
      return;
    }

    for (const stage of this.testCases) {
      this.log(`\n===== TESTING STAGE ${stage.stage}: ${stage.stageName} =====`);
      
      // Skip stages we've already completed
      if (stage.stage < this.currentSession.currentStage) {
        this.log(`Skipping stage ${stage.stage} (already completed)`);
        continue;
      }

      // If we're ahead of where we should be, something's wrong
      if (stage.stage > this.currentSession.currentStage) {
        this.logError(`Error: Current stage (${this.currentSession.currentStage}) doesn't match expected stage (${stage.stage})`);
        break;
      }

      // Run each test input for this stage
      for (const test of stage.testInputs) {
        await this.runSingleTest(stage, test);
      }
    }

    this.results.endTime = new Date().toISOString();
    this.log('\n===== TEST SUMMARY =====');
    this.log(`Tests run: ${this.results.tests.length}`);
    this.log(`Success: ${this.results.tests.filter(t => t.result === 'success').length}`);
    this.log(`Failures: ${this.results.tests.filter(t => t.result === 'failure').length}`);
    
    if (this.config.saveResults) {
      this.saveResults();
    }
  }

  /**
   * Run a single test case
   */
  async runSingleTest(stage, test) {
    this.log(`\nTest: ${test.label}`);
    this.log(`- Sending message: "${test.message}"`);
    
    const stageBeforeTest = this.currentSession.currentStage;
    const progressBeforeTest = this.currentSession.progress;
    
    try {
      // Send the test message
      const response = await fetch(`${this.config.apiBaseUrl}/consultation/chat?session_id=${this.currentSession.sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        body: JSON.stringify({
          content: test.message,
          role: 'user'
        })
      });

      const data = await response.json();
      
      // Update session information
      const newStage = data.template_progress.current_stage || this.currentSession.currentStage;
      const newProgress = data.template_progress.progress_percentage || this.currentSession.progress;
      const stageProgressed = newStage > stageBeforeTest;
      
      // Record results
      const result = {
        stageId: stage.stage,
        stageName: stage.stageName,
        testLabel: test.label,
        expectedProgression: test.expectProgression,
        actualProgression: stageProgressed,
        progressBefore: progressBeforeTest,
        progressAfter: newProgress,
        result: (stageProgressed === test.expectProgression) ? 'success' : 'failure',
        timestamp: new Date().toISOString(),
        aiResponseSummary: data.message.content.substring(0, 100) + '...',
        apiResponse: data
      };

      this.results.tests.push(result);
      
      // Update the current session state
      this.currentSession.currentStage = newStage;
      this.currentSession.progress = newProgress;

      // Log the result
      this.log(`- Stage progressed: ${stageProgressed ? 'YES' : 'NO'}`);
      this.log(`- Progress: ${progressBeforeTest}% → ${newProgress}%`);
      this.log(`- Expected progression: ${test.expectProgression ? 'YES' : 'NO'}`);
      this.log(`- Test result: ${result.result.toUpperCase()}`);

      if (result.result === 'failure') {
        this.logError(`- FAILURE: Stage ${stageProgressed ? 'progressed' : 'did not progress'} when we ${test.expectProgression ? 'expected' : 'did not expect'} progression`);
      }

      // If we've successfully progressed, we're done with this stage's tests
      if (stageProgressed) {
        this.log(`\n✅ Successfully progressed from stage ${stageBeforeTest} to stage ${newStage}`);
        return true;
      }
      
      return false;
    } catch (error) {
      this.logError('Test error:', error);
      return false;
    }
  }

  /**
   * Force progression to the next stage (for debugging)
   */
  async forceNextStage() {
    try {
      const response = await fetch(`${this.config.apiBaseUrl}/consultation/sessions/${this.currentSession.sessionId}/force-next-stage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        body: '{}'
      });

      const data = await response.json();
      
      // Update session information
      this.currentSession.currentStage = data.current_stage_index;
      this.currentSession.progress = data.progress_percentage;
      
      this.log(`Forced progression to stage ${this.currentSession.currentStage} (${data.progress_percentage}%)`);
      return data;
    } catch (error) {
      this.logError('Failed to force next stage:', error);
      return null;
    }
  }

  /**
   * Save test results to file (in a real browser, this would download a file)
   */
  saveResults() {
    console.log('RESULTS:', JSON.stringify(this.results, null, 2));
    this.log('Results saved to console (in production would save to ' + this.config.resultsFilePath + ')');
  }

  /**
   * Get the current stage progress
   */
  async getProgress() {
    try {
      const response = await fetch(`${this.config.apiBaseUrl}/consultation/sessions/${this.currentSession.sessionId}/progress`, {
        headers: {
          'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
      });

      return await response.json();
    } catch (error) {
      this.logError('Failed to get progress:', error);
      return null;
    }
  }

  /**
   * Log a debug message
   */
  log(message) {
    if (this.config.debugLogsEnabled) {
      console.log(message);
    }
    this.debugLogs.push({ time: new Date().toISOString(), message });
  }

  /**
   * Log an error message
   */
  logError(message, error) {
    console.error(message, error);
    this.debugLogs.push({ 
      time: new Date().toISOString(), 
      type: 'error', 
      message, 
      error: error?.toString() 
    });
  }
}

/**
 * UI component for running the tests from the browser
 * 
 * Usage:
 * 1. Copy this entire file content to your browser console
 * 2. Run: createTestUI()
 */
function createTestUI() {
  // Create UI container
  const uiContainer = document.createElement('div');
  uiContainer.style.position = 'fixed';
  uiContainer.style.bottom = '20px';
  uiContainer.style.right = '20px';
  uiContainer.style.width = '350px';
  uiContainer.style.backgroundColor = '#fff';
  uiContainer.style.border = '1px solid #ddd';
  uiContainer.style.borderRadius = '8px';
  uiContainer.style.padding = '15px';
  uiContainer.style.boxShadow = '0 0 15px rgba(0,0,0,0.2)';
  uiContainer.style.zIndex = '10000';
  uiContainer.style.fontFamily = 'Arial, sans-serif';
  uiContainer.style.fontSize = '14px';
  uiContainer.style.maxHeight = '80vh';
  uiContainer.style.overflowY = 'auto';

  // Create header
  const header = document.createElement('div');
  header.style.display = 'flex';
  header.style.justifyContent = 'space-between';
  header.style.alignItems = 'center';
  header.style.marginBottom = '15px';
  header.style.borderBottom = '1px solid #eee';
  header.style.paddingBottom = '10px';

  const title = document.createElement('h3');
  title.textContent = 'Stage Progression Tester';
  title.style.margin = '0';
  title.style.fontSize = '16px';
  title.style.fontWeight = 'bold';

  const closeBtn = document.createElement('button');
  closeBtn.textContent = '×';
  closeBtn.style.background = 'none';
  closeBtn.style.border = 'none';
  closeBtn.style.fontSize = '20px';
  closeBtn.style.cursor = 'pointer';
  closeBtn.style.padding = '0 5px';
  closeBtn.onclick = () => uiContainer.remove();

  header.appendChild(title);
  header.appendChild(closeBtn);
  uiContainer.appendChild(header);

  // Create test controls
  const controls = document.createElement('div');
  controls.style.marginBottom = '15px';

  // Initialize button
  const initBtn = document.createElement('button');
  initBtn.textContent = 'Initialize Test Session';
  initBtn.style.padding = '8px 12px';
  initBtn.style.marginRight = '10px';
  initBtn.style.backgroundColor = '#4CAF50';
  initBtn.style.color = 'white';
  initBtn.style.border = 'none';
  initBtn.style.borderRadius = '4px';
  initBtn.style.cursor = 'pointer';

  // Run All Tests button
  const runAllBtn = document.createElement('button');
  runAllBtn.textContent = 'Run All Tests';
  runAllBtn.style.padding = '8px 12px';
  runAllBtn.style.marginRight = '10px';
  runAllBtn.style.backgroundColor = '#2196F3';
  runAllBtn.style.color = 'white';
  runAllBtn.style.border = 'none';
  runAllBtn.style.borderRadius = '4px';
  runAllBtn.style.cursor = 'pointer';
  runAllBtn.disabled = true;

  // Force Next Stage button
  const forceNextBtn = document.createElement('button');
  forceNextBtn.textContent = 'Force Next Stage';
  forceNextBtn.style.padding = '8px 12px';
  forceNextBtn.style.backgroundColor = '#FF9800';
  forceNextBtn.style.color = 'white';
  forceNextBtn.style.border = 'none';
  forceNextBtn.style.borderRadius = '4px';
  forceNextBtn.style.cursor = 'pointer';
  forceNextBtn.disabled = true;

  controls.appendChild(initBtn);
  controls.appendChild(runAllBtn);
  controls.appendChild(forceNextBtn);
  uiContainer.appendChild(controls);

  // Stage status display
  const statusContainer = document.createElement('div');
  statusContainer.style.marginBottom = '15px';
  statusContainer.style.padding = '10px';
  statusContainer.style.backgroundColor = '#f5f5f5';
  statusContainer.style.borderRadius = '4px';
  statusContainer.style.fontSize = '13px';
  statusContainer.innerHTML = '<strong>Status:</strong> Not initialized';
  uiContainer.appendChild(statusContainer);

  // Results container
  const resultsContainer = document.createElement('div');
  resultsContainer.style.fontSize = '13px';
  resultsContainer.style.lineHeight = '1.4';
  resultsContainer.style.color = '#555';
  uiContainer.appendChild(resultsContainer);

  // Create the tester instance
  const tester = new StageProgressionTester();
  let isTestRunning = false;

  // Initialize button functionality
  initBtn.onclick = async () => {
    initBtn.disabled = true;
    resultsContainer.innerHTML = 'Initializing test session...';
    await tester.init();
    updateStatus();
    runAllBtn.disabled = false;
    forceNextBtn.disabled = false;
    resultsContainer.innerHTML = 'Test session initialized. Ready to run tests.';
  };

  // Run All Tests button functionality
  runAllBtn.onclick = async () => {
    if (isTestRunning) return;
    isTestRunning = true;
    runAllBtn.disabled = true;
    forceNextBtn.disabled = true;
    resultsContainer.innerHTML = 'Running all tests...';
    await tester.runAllTests();
    updateStatus();
    displayResults();
    runAllBtn.disabled = false;
    forceNextBtn.disabled = false;
    isTestRunning = false;
  };

  // Force Next Stage button functionality
  forceNextBtn.onclick = async () => {
    if (isTestRunning) return;
    resultsContainer.innerHTML = 'Forcing progression to next stage...';
    await tester.forceNextStage();
    updateStatus();
    resultsContainer.innerHTML += '<br>Forced progression complete.';
  };

  // Update status display
  async function updateStatus() {
    if (!tester.currentSession) {
      statusContainer.innerHTML = '<strong>Status:</strong> Not initialized';
      return;
    }

    const progressData = await tester.getProgress();
    statusContainer.innerHTML = `
      <strong>Status:</strong> Active<br>
      <strong>Session ID:</strong> ${tester.currentSession.sessionId}<br>
      <strong>Current Stage:</strong> ${tester.currentSession.currentStage}<br>
      <strong>Progress:</strong> ${tester.currentSession.progress}%
    `;
  }

  // Display test results
  function displayResults() {
    if (!tester.results || !tester.results.tests || tester.results.tests.length === 0) {
      resultsContainer.innerHTML = 'No test results available.';
      return;
    }

    let html = '<h4 style="margin-top:15px;margin-bottom:10px;">Test Results</h4>';
    html += '<div style="max-height:300px;overflow-y:auto;padding:10px;border:1px solid #eee;border-radius:4px;">';
    
    tester.results.tests.forEach(test => {
      const resultColor = test.result === 'success' ? '#4CAF50' : '#F44336';
      html += `
        <div style="margin-bottom:10px;padding:8px;border-left:3px solid ${resultColor};background-color:#f9f9f9;">
          <strong>Stage ${test.stageId}: ${test.stageName}</strong><br>
          <span style="font-size:12px;">${test.testLabel}</span><br>
          <span style="color:${resultColor};font-weight:bold;">${test.result.toUpperCase()}</span>
          <span style="font-size:12px;display:block;">Progress: ${test.progressBefore}% → ${test.progressAfter}%</span>
          <span style="font-size:12px;display:block;">Expected progression: ${test.expectedProgression ? 'YES' : 'NO'}</span>
          <span style="font-size:12px;display:block;">Actual progression: ${test.actualProgression ? 'YES' : 'NO'}</span>
        </div>
      `;
    });
    
    html += '</div>';
    
    // Add summary
    const successCount = tester.results.tests.filter(t => t.result === 'success').length;
    const failureCount = tester.results.tests.filter(t => t.result === 'failure').length;
    
    html += `
      <div style="margin-top:10px;padding:10px;background-color:#f0f0f0;border-radius:4px;">
        <strong>Summary:</strong> ${tester.results.tests.length} tests run<br>
        <span style="color:#4CAF50;">${successCount} passed</span>, 
        <span style="color:#F44336;">${failureCount} failed</span>
      </div>
    `;
    
    resultsContainer.innerHTML = html;
  }

  // Add to document
  document.body.appendChild(uiContainer);
  return uiContainer;
}

// Export functions for browser console
window.StageProgressionTester = StageProgressionTester;
window.createTestUI = createTestUI;
window.runStageTest = async function() {
  const tester = new StageProgressionTester();
  await tester.init();
  await tester.runAllTests();
  return tester.results;
};

// Usage instructions
console.log(`
Stage Progression Tester loaded!

To use in browser console:
1. Run "createTestUI()" to show the test panel
2. Click "Initialize Test Session" to start
3. Click "Run All Tests" to test all stage progressions
4. Use "Force Next Stage" to manually advance stages

For quick test run:
- Run "runStageTest()" to execute all tests and get results
`);