#!/usr/bin/env python3
"""
Test script for the orchestration agent functionality.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_orchestration_imports():
    """Test if all orchestration components import correctly."""
    try:
        from agents.crew_agents import (
            orchestration_crew,
            data_question_crew,
            alternative_viz_crew,
            follow_up_crew,
            OrchestrationDecision,
            DataQuestionAnswer,
            FollowUpQuestions
        )
        print("✅ All orchestration crews and models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_orchestration_crew():
    """Test the orchestration crew configuration."""
    try:
        from agents.crew_agents import orchestration_crew
        
        # Check if crew has the required agents and tasks
        print(f"📋 Orchestration crew agents: {len(orchestration_crew.agents)}")
        print(f"📋 Orchestration crew tasks: {len(orchestration_crew.tasks)}")
        
        if len(orchestration_crew.agents) > 0 and len(orchestration_crew.tasks) > 0:
            print("✅ Orchestration crew configured correctly")
            return True
        else:
            print("❌ Orchestration crew missing agents or tasks")
            return False
    except Exception as e:
        print(f"❌ Orchestration crew error: {e}")
        return False

def test_follow_up_crew():
    """Test the follow-up question crew."""
    try:
        from agents.crew_agents import follow_up_crew
        
        print(f"💡 Follow-up crew agents: {len(follow_up_crew.agents)}")
        print(f"💡 Follow-up crew tasks: {len(follow_up_crew.tasks)}")
        
        if len(follow_up_crew.agents) > 0 and len(follow_up_crew.tasks) > 0:
            print("✅ Follow-up crew configured correctly")
            return True
        else:
            print("❌ Follow-up crew missing agents or tasks")
            return False
    except Exception as e:
        print(f"❌ Follow-up crew error: {e}")
        return False

def main():
    """Run all orchestration tests."""
    print("🧪 Testing Orchestration Agent Implementation")
    print("=" * 50)
    
    tests = [
        test_orchestration_imports,
        test_orchestration_crew,
        test_follow_up_crew
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print("-" * 30)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All orchestration tests passed! The system is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
