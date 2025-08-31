import matplotlib.pyplot as plt
import numpy as np
import base64
import io

print("=== TEST IMAGE GENERATION ===")

# Create simple data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(x, y1, 'b-', label='Sin(x)', linewidth=2)
plt.plot(x, y2, 'r-', label='Cos(x)', linewidth=2)
plt.title('Simple Test Chart')
plt.xlabel('X values')
plt.ylabel('Y values')
plt.legend()
plt.grid(True, alpha=0.3)

# Convert to base64
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()
plt.close()

print("Chart created successfully!")
print(f"Image size: {len(image_base64)} characters")
print(f"IMAGE_BASE64:{image_base64}")
print("Test completed!")
