"""Main entry point for MAS Meal Recommendation System."""

import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

from memory.memory_manager import MemoryManager
from agents.orchestrator.agent import SystemOrchestrator


def main():
    """Main function to run the MAS system."""
    print("=" * 60)
    print("MAS-based Meal Recommendation System")
    print("=" * 60)
    print()
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  Warning: GOOGLE_API_KEY not found in environment variables.")
        print("   Please set GOOGLE_API_KEY in .env file")
        api_key = input("Enter your Google API key (or press Enter to continue with None): ").strip()
        if not api_key:
            api_key = None
    
    # Initialize memory manager
    memory_manager = MemoryManager(data_dir="data")
    
    # Initialize orchestrator
    orchestrator = SystemOrchestrator(memory_manager, api_key=api_key)
    
    print("✅ System initialized successfully!")
    print()
    print("You can now interact with the system.")
    print("Type 'quit' or 'exit' to stop.")
    print()
    
    # Interactive loop
    user_id = "default_user"
    
    while True:
        try:
            user_request = input("👤 You: ").strip()
            
            if user_request.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                # Clear STM at session end
                memory_manager.clear_stm()
                break
            
            if not user_request:
                continue
            
            print("\n🤖 Processing your request...\n")
            
            # Process request
            result = orchestrator.process({
                "user_request": user_request,
                "user_id": user_id
            })
            
            # Display results
            print("=" * 60)
            print("📋 RECOMMENDED MENU")
            print("=" * 60)
            
            final_menu = result.get("final_menu", {})
            menu = final_menu.get("menu", {})
            
            if menu:
                print(f"\n🍽️  {menu.get('name', 'Unknown')}")
                print(f"   Cuisine: {menu.get('cuisine', 'Unknown')}")
                print(f"\n📝 Ingredients:")
                for ingredient in menu.get("ingredients", []):
                    print(f"   - {ingredient}")
                
                print(f"\n👨‍🍳 Instructions:")
                for i, instruction in enumerate(menu.get("instructions", []), 1):
                    print(f"   {i}. {instruction}")
                
                nutrition = menu.get("nutrition", {})
                if nutrition:
                    print(f"\n📊 Nutrition (per serving):")
                    for key, value in nutrition.items():
                        print(f"   - {key}: {value}")
                
                print(f"\n💰 Total Cost: ₩{final_menu.get('total_cost', 0):,.0f}")
                print(f"   Serves: {menu.get('servings', 2)} people")
            
            # Show analysis
            pref_analysis = result.get("preference_analysis", {})
            if pref_analysis.get("warnings"):
                print(f"\n⚠️  Health Warnings:")
                for warning in pref_analysis["warnings"]:
                    print(f"   - {warning}")
            
            if pref_analysis.get("recommendations"):
                print(f"\n💡 Recommendations:")
                for rec in pref_analysis["recommendations"]:
                    print(f"   - {rec}")
            
            budget_analysis = result.get("budget_analysis", {})
            if not budget_analysis.get("within_budget"):
                print(f"\n💰 Budget Note: Estimated cost exceeds budget limit")
                suggestions = budget_analysis.get("suggestions", [])
                if suggestions:
                    for suggestion in suggestions:
                        print(f"   💡 {suggestion.get('message', '')}")
            
            print("\n" + "=" * 60)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            memory_manager.clear_stm()
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            print()


if __name__ == "__main__":
    main()

