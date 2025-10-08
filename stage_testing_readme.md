# Template Stage Progression Testing Tools

These tools help identify and debug issues with automatic stage progression in template consultations.

## Overview

We've created three different testing approaches, each suited for different scenarios:

1. **JavaScript Browser Console Tester** (`test_stage_progression.js`)
   - Injects a UI directly into the application
   - Tests with pre-defined inputs for each stage
   - Provides visual feedback on progression success/failure

2. **Backend Python Debugger** (`stage_progression_debug.py`)
   - Analyzes stage progression at the backend level
   - Monitors database state and traces AI service calls
   - Provides detailed logs and insights into progression issues

3. **Simple HTML Test UI** (`stage_tester_ui.html`)
   - Can be injected via browser console
   - Provides quick tests for each stage
   - Includes a "Force Next Stage" button for manual progression

## How to Use

### JavaScript Browser Console Tester

1. Open the browser console (F12 or Ctrl+Shift+I)
2. Copy the entire contents of `test_stage_progression.js`
3. Paste into the console and press Enter
4. Use the `createTestUI()` function to display the test panel
5. Follow the UI instructions to test stage progression

```javascript
// In browser console
createTestUI();
```

### Backend Python Debugger

1. Ensure you have administrative access to the backend
2. Edit the configuration in `stage_progression_debug.py` if needed
3. Run the script:

```bash
# Make sure the backend server is running
cd /home/nilabh/Projects/chakra
python3 stage_progression_debug.py
```

4. Check `stage_progression_debug.log` and `stage_progression_debug_results.json` for results

### Simple HTML Test UI

1. Open the browser console
2. Copy the entire contents of `stage_tester_ui.html`
3. Paste it into the console and press Enter
4. Use the buttons to test different stages or force progression

## Testing Strategy

When debugging stage progression issues, follow this process:

1. **Identify the problematic stage**: Use the Browser Console Tester to find which stages don't progress automatically.

2. **Test with various inputs**: Try different levels of completeness to see what triggers progression.

3. **Check backend logs**: Run the Python Debugger to see how the backend is processing stage transitions.

4. **Verify database state**: Look at how session_state is being updated after each message.

5. **Force progression**: Use the "Force Next Stage" button as a fallback for your demo.

## What to Look For

These are common issues that can prevent automatic stage progression:

1. **Threshold issues**: The AI may not recognize when all requirements are met
2. **Session state problems**: The database might not be updating correctly
3. **Template configuration**: The stage definitions may have unclear completion criteria
4. **Response processing**: The backend may not properly extract stage completion signals

## Solution

Our implemented solution adds a "Force Next Stage" feature that:

1. Makes a direct API call to `/consultation/sessions/{session_id}/force-next-stage`
2. Updates the UI with the new stage information
3. Allows the consultation to continue smoothly

This ensures demos can proceed even if automatic stage detection fails.