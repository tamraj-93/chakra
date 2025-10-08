"""
Sample consultation templates for demonstration purposes.
"""
import json
from pathlib import Path

# Health Consultation Template
HEALTH_CONSULTATION = {
    "name": "Health Symptom Assessment",
    "description": "A structured consultation for assessing health symptoms and providing preliminary guidance.",
    "domain": "healthcare",
    "version": "1.0",
    "tags": ["healthcare", "symptoms", "assessment", "medical"],
    "initial_system_prompt": "You are a healthcare assistant designed to help gather information about symptoms and provide preliminary guidance. You are NOT a doctor and cannot provide medical diagnoses. Always recommend consulting a healthcare professional for proper medical advice.",
    "stages": [
        {
            "name": "Symptom Gathering",
            "description": "Collect initial symptoms from the patient",
            "stage_type": "information_gathering",
            "prompt_template": "Please ask the user about their main symptoms. Focus on gathering: 1) Main complaint, 2) Duration of symptoms, 3) Severity (on scale 1-10), 4) Any factors that make it better or worse.",
            "system_instructions": "Be empathetic and thorough. Ask one question at a time. Make sure to get specific details about timing, severity, and factors affecting symptoms.",
            "expected_outputs": [
                {
                    "name": "primary_symptom",
                    "description": "The main symptom the patient is experiencing",
                    "data_type": "text",
                    "required": True
                },
                {
                    "name": "duration",
                    "description": "How long the patient has been experiencing the symptom",
                    "data_type": "text",
                    "required": True
                },
                {
                    "name": "severity",
                    "description": "Severity of the symptom on scale 1-10",
                    "data_type": "number",
                    "required": True
                }
            ],
            "ui_components": {
                "progress_indicator": True,
                "symptom_checklist": True
            },
            "next_stage_conditions": {
                "default": "Medical History"
            }
        },
        {
            "name": "Medical History",
            "description": "Gather relevant medical history",
            "stage_type": "information_gathering",
            "prompt_template": "Now ask about relevant medical history: 1) Previous similar episodes, 2) Known medical conditions, 3) Current medications, 4) Allergies.",
            "system_instructions": "Focus on information relevant to the symptoms already described. Be concise but thorough.",
            "expected_outputs": [
                {
                    "name": "previous_episodes",
                    "description": "Whether the patient has experienced these symptoms before",
                    "data_type": "text",
                    "required": True
                },
                {
                    "name": "medical_conditions",
                    "description": "Pre-existing medical conditions",
                    "data_type": "list",
                    "required": False
                },
                {
                    "name": "medications",
                    "description": "Current medications",
                    "data_type": "list",
                    "required": False
                }
            ],
            "ui_components": {
                "progress_indicator": True,
                "medical_history_form": True
            },
            "next_stage_conditions": {
                "default": "Risk Assessment"
            }
        },
        {
            "name": "Risk Assessment",
            "description": "Assess whether urgent care is needed",
            "stage_type": "problem_analysis",
            "prompt_template": "Based on the information gathered, assess if there are any red flags that require urgent medical attention. Check for: severe pain, difficulty breathing, changes in consciousness, or other concerning symptoms.",
            "system_instructions": "Err on the side of caution. If there are any concerning symptoms that might require urgent care, clearly state this. Never discourage seeking medical help.",
            "expected_outputs": [
                {
                    "name": "urgency_level",
                    "description": "Assessment of how urgently medical care is needed",
                    "data_type": "text",
                    "required": True
                },
                {
                    "name": "red_flags",
                    "description": "Any concerning symptoms that require urgent attention",
                    "data_type": "list",
                    "required": False
                }
            ],
            "ui_components": {
                "urgency_indicator": True,
                "warning_banner": True
            },
            "next_stage_conditions": {
                "default": "Recommendations"
            }
        },
        {
            "name": "Recommendations",
            "description": "Provide guidance based on the assessment",
            "stage_type": "recommendation",
            "prompt_template": "Based on all information gathered, provide: 1) General guidance for symptom management, 2) When to seek medical care, 3) Potential next steps.",
            "system_instructions": "Be clear and actionable. Always emphasize the importance of professional medical advice. Never diagnose. Focus on general wellness and symptom management strategies.",
            "expected_outputs": [
                {
                    "name": "management_strategies",
                    "description": "Suggestions for managing symptoms",
                    "data_type": "list",
                    "required": True
                },
                {
                    "name": "when_to_seek_care",
                    "description": "Guidance on when to consult a healthcare professional",
                    "data_type": "text",
                    "required": True
                },
                {
                    "name": "next_steps",
                    "description": "Recommended actions",
                    "data_type": "list",
                    "required": True
                }
            ],
            "ui_components": {
                "recommendation_cards": True,
                "action_checklist": True,
                "download_summary": True
            },
            "next_stage_conditions": {
                "default": "Summary"
            }
        },
        {
            "name": "Summary",
            "description": "Summarize the consultation",
            "stage_type": "summary",
            "prompt_template": "Create a concise summary of the consultation, including: 1) Main symptoms, 2) Key points from history, 3) Recommendations provided.",
            "system_instructions": "Be brief but comprehensive. Format the summary in a way that's easy to read and reference later.",
            "expected_outputs": [
                {
                    "name": "consultation_summary",
                    "description": "Complete summary of the consultation",
                    "data_type": "text",
                    "required": True
                }
            ],
            "ui_components": {
                "summary_card": True,
                "export_options": True
            },
            "next_stage_conditions": {}
        }
    ]
}

# Tech Support Template
TECH_SUPPORT_CONSULTATION = {
    "name": "Technical Issue Troubleshooting",
    "description": "A guided technical support consultation for diagnosing and resolving common technical issues.",
    "domain": "tech_support",
    "version": "1.0",
    "tags": ["technical", "troubleshooting", "IT support", "diagnostics"],
    "initial_system_prompt": "You are a technical support assistant designed to help users diagnose and resolve technical issues. Focus on clear communication, structured problem-solving, and providing actionable solutions.",
    "stages": [
        {
            "name": "Problem Identification",
            "description": "Identify the core technical issue",
            "stage_type": "information_gathering",
            "prompt_template": "Ask the user to describe the technical issue they're experiencing. Focus on: 1) What device/software is involved, 2) Exact error messages if any, 3) When the problem started, 4) What they were doing when it occurred.",
            "system_instructions": "Be precise in your questions. Technical details are crucial for accurate diagnosis. Ask for screenshots or exact error messages when applicable.",
            "expected_outputs": [
                {
                    "name": "device_software",
                    "description": "The device or software experiencing the issue",
                    "data_type": "text",
                    "required": True
                },
                {
                    "name": "error_message",
                    "description": "Any error messages displayed",
                    "data_type": "text",
                    "required": False
                },
                {
                    "name": "issue_description",
                    "description": "Description of what's happening",
                    "data_type": "text",
                    "required": True
                }
            ],
            "ui_components": {
                "issue_form": True,
                "screenshot_upload": True
            },
            "next_stage_conditions": {
                "default": "System Information"
            }
        },
        {
            "name": "System Information",
            "description": "Gather relevant system details",
            "stage_type": "information_gathering",
            "prompt_template": "Ask for relevant system information: 1) Operating system version, 2) Device model if applicable, 3) Software version if applicable, 4) Recent updates or changes.",
            "system_instructions": "Guide the user on how to find this information if they don't know how. Focus only on information relevant to the specific issue.",
            "expected_outputs": [
                {
                    "name": "operating_system",
                    "description": "Operating system and version",
                    "data_type": "text",
                    "required": False
                },
                {
                    "name": "software_version",
                    "description": "Version of the software having issues",
                    "data_type": "text",
                    "required": False
                },
                {
                    "name": "recent_changes",
                    "description": "Recent system changes or updates",
                    "data_type": "text",
                    "required": False
                }
            ],
            "ui_components": {
                "system_info_form": True
            },
            "next_stage_conditions": {
                "default": "Troubleshooting Steps"
            }
        },
        {
            "name": "Troubleshooting Steps",
            "description": "Guide the user through diagnostic steps",
            "stage_type": "problem_analysis",
            "prompt_template": "Based on the information gathered, suggest initial troubleshooting steps. Provide clear, step-by-step instructions that the user can follow. Ask them to report results after each significant step.",
            "system_instructions": "Start with simple solutions before complex ones. Provide numbered steps. Check if each step resolved the issue before moving to the next one.",
            "expected_outputs": [
                {
                    "name": "initial_diagnosis",
                    "description": "Initial assessment of the problem",
                    "data_type": "text",
                    "required": True
                },
                {
                    "name": "troubleshooting_results",
                    "description": "Results of the troubleshooting steps",
                    "data_type": "object",
                    "required": True
                }
            ],
            "ui_components": {
                "step_by_step_guide": True,
                "progress_tracker": True
            },
            "next_stage_conditions": {
                "issue_resolved": "Resolution",
                "default": "Advanced Troubleshooting"
            }
        },
        {
            "name": "Advanced Troubleshooting",
            "description": "More advanced diagnostic steps if initial troubleshooting fails",
            "stage_type": "problem_analysis",
            "prompt_template": "Since the initial steps didn't resolve the issue, let's try more advanced troubleshooting. These steps may be more technical or time-consuming.",
            "system_instructions": "Be even more detailed with instructions for advanced steps. Warn the user about any potential risks. Consider suggesting professional support if appropriate.",
            "expected_outputs": [
                {
                    "name": "advanced_diagnosis",
                    "description": "More detailed assessment of the problem",
                    "data_type": "text",
                    "required": True
                },
                {
                    "name": "advanced_results",
                    "description": "Results of advanced troubleshooting",
                    "data_type": "object",
                    "required": True
                }
            ],
            "ui_components": {
                "advanced_steps_guide": True,
                "warning_notices": True
            },
            "next_stage_conditions": {
                "default": "Resolution"
            }
        },
        {
            "name": "Resolution",
            "description": "Provide final solution and preventative advice",
            "stage_type": "recommendation",
            "prompt_template": "Summarize the resolution or best next steps. Include: 1) What fixed the issue or next steps if unresolved, 2) How to prevent this issue in the future, 3) Any additional recommendations.",
            "system_instructions": "Be clear about whether the issue was resolved or not. If not fully resolved, be honest and suggest professional support if appropriate.",
            "expected_outputs": [
                {
                    "name": "resolution_status",
                    "description": "Whether and how the issue was resolved",
                    "data_type": "text",
                    "required": True
                },
                {
                    "name": "prevention_tips",
                    "description": "How to prevent the issue in future",
                    "data_type": "list",
                    "required": True
                }
            ],
            "ui_components": {
                "resolution_card": True,
                "feedback_form": True,
                "prevention_checklist": True
            },
            "next_stage_conditions": {
                "default": "Summary"
            }
        },
        {
            "name": "Summary",
            "description": "Summarize the troubleshooting session",
            "stage_type": "summary",
            "prompt_template": "Create a technical support summary including: 1) Initial problem, 2) Key troubleshooting steps performed, 3) Resolution status and next steps.",
            "system_instructions": "Format as a technical report. Include all relevant details that might be useful for future reference or for escalating to more advanced support.",
            "expected_outputs": [
                {
                    "name": "support_summary",
                    "description": "Complete summary of the support session",
                    "data_type": "text",
                    "required": True
                }
            ],
            "ui_components": {
                "tech_report": True,
                "export_options": True
            },
            "next_stage_conditions": {}
        }
    ]
}

# Financial Advisory Template
FINANCIAL_ADVISORY_CONSULTATION = {
    "name": "Financial Goal Planning",
    "description": "A structured consultation to help users assess financial goals and develop action plans.",
    "domain": "financial_advisory",
    "version": "1.0",
    "tags": ["finance", "planning", "goals", "investment", "budgeting"],
    "initial_system_prompt": "You are a financial planning assistant designed to help users clarify financial goals and develop action plans. You are NOT a licensed financial advisor and cannot provide personalized investment advice. Always recommend consulting with a financial professional for specific investment decisions.",
    "stages": [
        {
            "name": "Goal Identification",
            "description": "Identify financial goals and priorities",
            "stage_type": "information_gathering",
            "prompt_template": "Ask the user about their financial goals. Focus on: 1) Short-term goals (within 1 year), 2) Medium-term goals (1-5 years), 3) Long-term goals (5+ years), 4) Priority ranking of these goals.",
            "system_instructions": "Help the user articulate specific, measurable goals with timeframes. Avoid vague goals like 'be wealthy' and encourage more specific ones like 'save $10,000 for a home down payment within 2 years'.",
            "expected_outputs": [
                {
                    "name": "short_term_goals",
                    "description": "Financial goals within 1 year",
                    "data_type": "list",
                    "required": False
                },
                {
                    "name": "medium_term_goals",
                    "description": "Financial goals within 1-5 years",
                    "data_type": "list",
                    "required": False
                },
                {
                    "name": "long_term_goals",
                    "description": "Financial goals beyond 5 years",
                    "data_type": "list",
                    "required": False
                },
                {
                    "name": "top_priority",
                    "description": "Highest priority financial goal",
                    "data_type": "text",
                    "required": True
                }
            ],
            "ui_components": {
                "goal_timeline": True,
                "priority_ranking": True
            },
            "next_stage_conditions": {
                "default": "Financial Situation"
            }
        },
        {
            "name": "Financial Situation",
            "description": "Assess current financial status",
            "stage_type": "information_gathering",
            "prompt_template": "Now let's understand your current financial situation. Please share: 1) Current income streams, 2) Major expense categories, 3) Existing savings and investments, 4) Outstanding debts.",
            "system_instructions": "Be sensitive about financial information. Offer ranges or percentages as alternatives if users are uncomfortable sharing exact figures. Focus on the big picture rather than specific account details.",
            "expected_outputs": [
                {
                    "name": "income_summary",
                    "description": "Summary of income sources",
                    "data_type": "text",
                    "required": True
                },
                {
                    "name": "expense_summary",
                    "description": "Summary of major expenses",
                    "data_type": "text",
                    "required": True
                },
                {
                    "name": "savings_summary",
                    "description": "Overview of savings and investments",
                    "data_type": "text",
                    "required": False
                },
                {
                    "name": "debt_summary",
                    "description": "Overview of outstanding debts",
                    "data_type": "text",
                    "required": False
                }
            ],
            "ui_components": {
                "financial_snapshot": True,
                "income_expense_ratio": True
            },
            "next_stage_conditions": {
                "default": "Gap Analysis"
            }
        },
        {
            "name": "Gap Analysis",
            "description": "Analyze gaps between current situation and goals",
            "stage_type": "problem_analysis",
            "prompt_template": "Based on your financial goals and current situation, let's identify the gaps and challenges. What obstacles might prevent you from reaching your goals? What resources or changes might be needed?",
            "system_instructions": "Be realistic but constructive. Identify specific gaps in savings rates, income needs, or timeline adjustments that might be necessary. Don't focus only on problems - also identify strengths and opportunities.",
            "expected_outputs": [
                {
                    "name": "key_gaps",
                    "description": "Major gaps between current state and goals",
                    "data_type": "list",
                    "required": True
                },
                {
                    "name": "strengths",
                    "description": "Financial strengths and opportunities",
                    "data_type": "list",
                    "required": True
                }
            ],
            "ui_components": {
                "gap_analysis_chart": True,
                "strength_weakness_grid": True
            },
            "next_stage_conditions": {
                "default": "Action Plan"
            }
        },
        {
            "name": "Action Plan",
            "description": "Develop an action plan to achieve financial goals",
            "stage_type": "recommendation",
            "prompt_template": "Let's create an action plan to help you achieve your financial goals. For each goal, we'll outline specific steps, timelines, and resources needed.",
            "system_instructions": "Provide specific, actionable steps. Include both quick wins and longer-term strategies. Recommend general approaches like budgeting techniques, saving strategies, or debt reduction methods, but avoid specific investment recommendations.",
            "expected_outputs": [
                {
                    "name": "immediate_actions",
                    "description": "Steps to take within the next 30 days",
                    "data_type": "list",
                    "required": True
                },
                {
                    "name": "medium_term_actions",
                    "description": "Steps to take within 1-6 months",
                    "data_type": "list",
                    "required": True
                },
                {
                    "name": "long_term_strategy",
                    "description": "Ongoing strategies for long-term success",
                    "data_type": "list",
                    "required": True
                }
            ],
            "ui_components": {
                "action_timeline": True,
                "task_checklist": True,
                "milestone_tracker": True
            },
            "next_stage_conditions": {
                "default": "Resources"
            }
        },
        {
            "name": "Resources",
            "description": "Provide helpful resources and tools",
            "stage_type": "recommendation",
            "prompt_template": "Let me suggest some resources that might help you implement your financial plan. These might include budgeting tools, educational resources, or types of professionals to consult.",
            "system_instructions": "Focus on general categories of resources rather than specific brands or companies. Emphasize free or low-cost options when available. Include both digital tools and human resources.",
            "expected_outputs": [
                {
                    "name": "recommended_tools",
                    "description": "Suggested tools and applications",
                    "data_type": "list",
                    "required": True
                },
                {
                    "name": "educational_resources",
                    "description": "Learning materials and sources",
                    "data_type": "list",
                    "required": True
                },
                {
                    "name": "professional_support",
                    "description": "Types of professionals to consider consulting",
                    "data_type": "list",
                    "required": True
                }
            ],
            "ui_components": {
                "resource_library": True,
                "professional_directory": True
            },
            "next_stage_conditions": {
                "default": "Summary"
            }
        },
        {
            "name": "Summary",
            "description": "Summarize the financial planning session",
            "stage_type": "summary",
            "prompt_template": "Let's summarize our financial planning discussion, including: 1) Your key goals, 2) Current situation highlights, 3) Action plan summary, 4) Next steps and timeline.",
            "system_instructions": "Create a concise but comprehensive summary. Format it in a way that serves as a quick reference document. Emphasize action items and next steps.",
            "expected_outputs": [
                {
                    "name": "planning_summary",
                    "description": "Complete summary of the financial planning session",
                    "data_type": "text",
                    "required": True
                }
            ],
            "ui_components": {
                "financial_plan_document": True,
                "export_options": True,
                "calendar_integration": True
            },
            "next_stage_conditions": {}
        }
    ]
}


def save_templates():
    """Save the sample templates to JSON files in the examples directory."""
    templates = {
        "health_consultation.json": HEALTH_CONSULTATION,
        "tech_support.json": TECH_SUPPORT_CONSULTATION,
        "financial_advisory.json": FINANCIAL_ADVISORY_CONSULTATION
    }
    
    # Ensure the examples directory exists
    examples_dir = Path(__file__).resolve().parent.parent.parent.parent / "examples"
    examples_dir.mkdir(exist_ok=True)
    
    for filename, template in templates.items():
        file_path = examples_dir / filename
        with open(file_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"Saved template to {file_path}")


if __name__ == "__main__":
    save_templates()