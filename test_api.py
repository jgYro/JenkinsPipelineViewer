#!/usr/bin/env python3
import requests
import json
from pprint import pprint

# Test the Flask API
try:
    # Test get_pipeline endpoint (simulating what React would do)
    print("=== Testing Flask Backend ===")
    
    # Import and call get_pipeline directly
    import sys
    sys.path.append('.')
    from app import get_pipeline
    
    pipeline_data = get_pipeline()
    
    print("\n=== Pipeline Data ===")
    print(f"Run Info: {pipeline_data['runInfo']['id']} - {pipeline_data['runInfo']['status']}")
    print(f"Duration: {pipeline_data['runInfo']['durationMillis']}ms")
    
    print("\n=== Stages ===")
    for stage in pipeline_data['stages']:
        print(f"\nStage: {stage['name']} [{stage['status']}]")
        for step in stage['stageFlowNodes']:
            print(f"  - {step['name']}: {step['status']}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()