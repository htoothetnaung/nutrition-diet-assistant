"""
Simple test script for NutriNet Food Vision (Food-101 only)
Run this to verify the system works before integrating with app.py
"""

from food_vision import NutriNetVision
import os


def test_system():
    print("🧪 Testing NutriNet Food Vision System (Food-101)")
    print("=" * 50)

    # Check model file
    print("📁 Checking Food-101 model file...")
    food101_path = "model_weights/food101_model.pth"

    if os.path.exists(food101_path):
        print(f"✅ Food-101 model found: {food101_path}")
    else:
        print(f"⚠️  Food-101 model not found: {food101_path}")
        print("   Please place your weights at this path.")

    print()

    # Test initialization
    print("🔧 Testing system initialization...")
    try:
        nutrinet = NutriNetVision()
        print("✅ NutriNet system initialized successfully!")
        print()

        # Test with a sample image if available
        test_img_dir = "test_imgs"
        if os.path.exists(test_img_dir):
            test_images = [
                f
                for f in os.listdir(test_img_dir)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            ]

            if test_images:
                print(f"📸 Found {len(test_images)} test images in {test_img_dir}")
                print("   You can now integrate this with your app.py!")
                print()
                print("🎯 Integration ready! Use NutriNetVision.analyze_image(image)")
            else:
                print(f"📸 No test images found in {test_img_dir}")
                print("   Create the directory and add some food images to test")
        else:
            print(f"📸 Test images directory {test_img_dir} not found")
            print("   Create the directory and add some food images to test")

    except Exception as e:
        print(f"❌ Failed to initialize NutriNet: {str(e)}")
        print("   Please check that all dependencies are installed")
        print("   Run: pip install torch torchvision pillow")


if __name__ == "__main__":
    test_system()
