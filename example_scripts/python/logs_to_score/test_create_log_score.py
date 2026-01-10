#!/usr/bin/env python3
"""Test script for creating log scores."""

from basic_logging import create_log
from create_evaluator import create_llm_evaluator
from create_log_scores import create_log_score
from dotenv import load_dotenv
import time

load_dotenv(override=True)

print('=' * 80)
print('Testing Create Log Score - Complete Workflow')
print('=' * 80)

# Step 1: Create a log
print('\n📝 Step 1: Creating a log...')
log_data = create_log(
    model='gpt-4o',
    input_messages=[{'role': 'user', 'content': 'What is machine learning?'}],
    output_message={
        'role': 'assistant', 
        'content': 'Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.'
    },
    custom_identifier=f'test_score_log_{int(time.time())}'
)
log_id = log_data.get('unique_id')
print(f'✓ Log created with ID: {log_id}')

# Step 2: Create an evaluator
print('\n📊 Step 2: Creating an evaluator...')
evaluator_data = create_llm_evaluator(
    name='Test Response Quality Evaluator',
    evaluator_slug=f'test_response_quality_{int(time.time())}',
    evaluator_definition=(
        'Evaluate the response quality based on accuracy and completeness.\n'
        '<llm_input>{{input}}</llm_input>\n'
        '<llm_output>{{output}}</llm_output>'
    ),
    scoring_rubric='0.0=Poor, 0.5=Average, 1.0=Excellent',
    description='Test evaluator for log scoring'
)
evaluator_slug = evaluator_data.get('evaluator_slug')
print(f'✓ Evaluator created with slug: {evaluator_slug}')

# Step 3: Wait a moment
print('\n⏳ Waiting 2 seconds for processing...')
time.sleep(2)

# Step 4: Create a score on the log
print('\n⭐ Step 3: Creating score on the log...')
try:
    score_data = create_log_score(
        log_id=log_id,
        evaluator_slug=evaluator_slug,
        score=0.85,
        reasoning='The response accurately explains machine learning and provides a clear, complete definition.'
    )
    print(f'\n✅ SUCCESS! Score created!')
    print(f'Score ID: {score_data.get("id", "N/A")}')
    # Show the correct value field
    if score_data.get('numerical_value') is not None:
        print(f'Score Value (numerical): {score_data.get("numerical_value")}')
    elif score_data.get('string_value'):
        print(f'Score Value (string): {score_data.get("string_value")}')
    elif score_data.get('boolean_value') is not None:
        print(f'Score Value (boolean): {score_data.get("boolean_value")}')
    print(f'\n{"="*80}')
    print('Test completed successfully!')
    print(f'{"="*80}')
except Exception as e:
    print(f'\n❌ Error creating score: {e}')
    import traceback
    traceback.print_exc()
