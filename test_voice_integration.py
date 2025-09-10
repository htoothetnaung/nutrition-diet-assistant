#!/usr/bin/env python3
"""
Test script to verify voice assistant integration
"""

import os
import sys


def test_voice_assistant_import():
    """Test if voice assistant can be imported"""
    try:
        from assembly_nutrition_assistant import AssemblyNutritionAssistant

        print("✅ Successfully imported AssemblyNutritionAssistant")
        return True
    except ImportError as e:
        print(f"❌ Failed to import AssemblyNutritionAssistant: {e}")
        return False


def test_voice_dependencies():
    """Test if voice assistant dependencies are available"""
    dependencies = ["vosk", "sounddevice", "pyttsx3", "assemblyai"]

    missing_deps = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} is available")
        except ImportError:
            print(f"❌ {dep} is missing")
            missing_deps.append(dep)

    return len(missing_deps) == 0


def test_model_files():
    """Test if required model files exist"""
    model_path = os.path.join(
        os.path.dirname(__file__),
        "vosk-model-small-en-us-0.15",
        "vosk-model-small-en-us-0.15",
    )
    kb_path = os.path.join(
        os.path.dirname(__file__), "models", "accurate_nutrition_kb.json"
    )

    if os.path.exists(model_path):
        print("✅ Vosk model directory exists")
    else:
        print(f"❌ Vosk model directory not found at: {model_path}")
        return False

    if os.path.exists(kb_path):
        print("✅ Nutrition knowledge base exists")
    else:
        print(f"❌ Nutrition knowledge base not found at: {kb_path}")
        return False

    return True


def test_voice_assistant_initialization():
    """Test if voice assistant can be initialized"""
    try:
        from assembly_nutrition_assistant import AssemblyNutritionAssistant

        model_path = os.path.join(
            os.path.dirname(__file__),
            "vosk-model-small-en-us-0.15",
            "vosk-model-small-en-us-0.15",
        )
        kb_path = os.path.join(
            os.path.dirname(__file__), "models", "accurate_nutrition_kb.json"
        )

        # Set API key
        os.environ["ASSEMBLYAI_API_KEY"] = "32a11032d56d438497638cd2b8e6fd5a"

        assistant = AssemblyNutritionAssistant(
            model_path=model_path,
            assembly_key="32a11032d56d438497638cd2b8e6fd5a",
            nutrition_kb_path=kb_path,
        )

        print("✅ Voice assistant initialized successfully")
        assistant.cleanup()
        return True

    except Exception as e:
        print(f"❌ Failed to initialize voice assistant: {e}")
        return False


def main():
    print("🧪 Testing Voice Assistant Integration")
    print("=" * 50)

    tests = [
        ("Dependencies", test_voice_dependencies),
        ("Model Files", test_model_files),
        ("Import", test_voice_assistant_import),
        ("Initialization", test_voice_assistant_initialization),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Voice assistant integration is ready.")
        print("\n🚀 To run the Streamlit app with voice assistant:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 To install missing dependencies:")
        print("   pip install vosk sounddevice pyttsx3 assemblyai")


if __name__ == "__main__":
    main()
