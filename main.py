import streamlit as st
import pandas as pd
import json
import hashlib
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go
import base64
from PIL import Image
import io
import os

# Page configuration
st.set_page_config(
    page_title="TechMart - Your Online Store",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_image_as_base64(image_path):
    """
    Load local image file and convert to base64 string for display

    USAGE: Replace 'image_path' with your actual image file paths
    EXAMPLE: load_image_as_base64("assets/products/macbook.jpg")

    SUPPORTED FORMATS: JPG, PNG, GIF, WEBP
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None


def get_image_html(image_data, width="200px", height="200px"):
    """
    Create HTML img tag for displaying images

    PARAMETERS:
    - image_data: base64 string or URL or file path
    - width/height: CSS dimensions for the image

    CUSTOMIZATION: Change width/height for different product card sizes
    """
    if image_data:
        if image_data.startswith('data:image') or image_data.startswith('http'):
            src = image_data
        elif os.path.exists(image_data):
            try:
                with open(image_data, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    ext = image_data.split('.')[-1].lower()
                    if ext in ['jpg', 'jpeg']:
                        src = f"data:image/jpeg;base64,{b64}"
                    elif ext == 'png':
                        src = f"data:image/png;base64,{b64}"
                    else:
                        src = f"data:image/{ext};base64,{b64}"
            except:
                return f'<div style="width:{width};height:{height};background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:8px;">📷 No Image</div>'
        else:
            return f'<div style="width:{width};height:{height};display:flex;align-items:center;justify-content:center;font-size:4rem;background:#f8f9fa;border-radius:8px;">{image_data}</div>'
    else:
        return f'<div style="width:{width};height:{height};background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:8px;color:#666;">📷 No Image</div>'

    return f'<img src="{src}" style="width:{width};height:{height};object-fit:cover;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);" />'


def save_uploaded_image(uploaded_file, product_id):
    """
    Save uploaded image file and return the file path

    DIRECTORY STRUCTURE:
    Create these folders in your project:
    - assets/
      - products/
        - product_images/

    USAGE: This function saves uploaded images to local directory
    """
    if uploaded_file is not None:
        # Create directory if it doesn't exist
        os.makedirs("../assets/products/product_images", exist_ok=True)

        # Generate filename
        file_extension = uploaded_file.name.split('.')[-1]
        filename = f"{product_id}.{file_extension}"
        file_path = f"../assets/products/product_images/{filename}"

        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return file_path
    return None

st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        position: sticky;  /* makes it stick */
        top: 0;            /* stick to top */
        z-index: 9999;     /* stay above everything */

        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        padding: 1.5rem;
        border-radius: 0 0 16px 16px;  /* rounded only at bottom */
        margin-bottom: 2.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }

    .main-header h1 {
        font-size: 2.2rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: 1px;
    }

    /* Product card modern design */
    .product-card {
        border: none;
        border-radius: 20px;
        padding: 1.8rem;
        margin: 1.2rem 0;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }

    /* Hover effect */
    .product-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.18);
    }

    /* Product image styling */
    .product-card img {
        max-width: 100%;
        border-radius: 15px;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }

    .product-card:hover img {
        transform: scale(1.05);
    }

    /* Product title */
    .product-card h3 {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #333;
    }

    /* Price styling */
    .product-card .price {
        font-size: 1.1rem;
        font-weight: bold;
        color: #2575fc;
        margin-bottom: 1rem;
    }

    /* Buy button */
    .product-card button {
        background: linear-gradient(135deg, #2575fc 0%, #6a11cb 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-size: 1rem;
        cursor: pointer;
        transition: background 0.3s ease, transform 0.2s ease;
    }

    .product-card button:hover {
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        transform: scale(1.05);
    }

    /* Image container for consistent sizing */
    .product-image-container {
        text-align: center;
        margin-bottom: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
    }

    /* Cart and order items */
    .cart-item {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }

    .cart-item-image {
        width: 80px;
        height: 80px;
        object-fit: cover;
        border-radius: 8px;
        margin-right: 1rem;
    }

    /* Metrics and alerts */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }

    .warning-message {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
    }

    /* Admin panel styling */
    .admin-image-preview {
        max-width: 150px;
        max-height: 150px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'users' not in st.session_state:
        st.session_state.users = {}

    if 'products' not in st.session_state:
        # =====================================================================
        # PRODUCT IMAGES CONFIGURATION
        # =====================================================================
        #
        # HOW TO ADD YOUR OWN IMAGES:
        #
        # 1. EMOJI METHOD (Current):
        #    - Keep the current emoji system for quick demo
        #    - Just change the 'image' value to any emoji
        #
        # 2. LOCAL FILES METHOD:
        #    - Create folder: assets/products/
        #    - Add your images: macbook.jpg, iphone.png, etc.
        #    - Change 'image' value to: "assets/products/macbook.jpg"
        #
        # 3. ONLINE IMAGES METHOD:
        #    - Use direct URLs: "https://example.com/image.jpg"
        #    - Change 'image' value to the full URL
        #
        # 4. BASE64 METHOD:
        #    - Convert images to base64 strings
        #    - Use online converters or Python script
        #    - Change 'image' value to: "data:image/jpeg;base64,YOUR_BASE64_STRING"
        #
        # =====================================================================

        st.session_state.products = {
            'P001': {
                'name': 'MacBook Pro 14"',
                'price': 1999.99,
                'category': 'Electronics',
                'description': 'Apple M2 Pro chip, 16GB RAM, 512GB SSD. Perfect for developers and creative professionals.',
                'stock': 15,
                'image': 'assets/products/macbook-pro-og-202410.jpeg',
                'rating': 4.8,
                'reviews': 245,
                'specs': ['M2 Pro Chip', '16GB RAM', '512GB SSD', '14" Display']
            },
            'P002': {
                'name': 'iPhone 15 Pro',
                'price': 999.99,
                'category': 'Electronics',
                'description': 'A17 Pro chip, 128GB storage, Titanium design with advanced camera system.',
                'stock': 30,
                'image': 'assets/products/iPhone_15_Pro_Black_Titanium_PDP_Image_Position-5__en-IN_40f33ec2-8463-4813-b046-57489b93585e.jpg.webp',
                'rating': 4.7,
                'reviews': 189,
                'specs': ['A17 Pro Chip', '128GB Storage', 'Titanium Build', 'Pro Camera']
            },
            'P003': {
                'name': 'Nike Air Max 270',
                'price': 129.99,
                'category': 'Footwear',
                'description': 'Comfortable running shoes with Air Max technology and modern design.',
                'stock': 50,
                'image': 'assets/products/Unknown.jpeg',
                'rating': 4.5,
                'reviews': 334,
                'specs': ['Air Max Technology', 'Mesh Upper', 'Foam Midsole', 'Rubber Outsole']
            },
            'P004': {
                'name': 'Sony WH-1000XM5',
                'price': 399.99,
                'category': 'Electronics',
                'description': 'Industry-leading wireless noise-canceling headphones with 30-hour battery life.',
                'stock': 25,
                'image': 'assets/products/images.jpg',
                'rating': 4.9,
                'reviews': 156,
                'specs': ['Noise Canceling', '30hr Battery', 'Quick Charge', 'Touch Controls']
            },
            'P005': {
                'name': 'Levi\'s 511 Slim Jeans',
                'price': 69.99,
                'category': 'Clothing',
                'description': 'Classic slim-fit denim jeans made from premium cotton blend.',
                'stock': 40,
                'image': 'assets/products/-473Wx593H-469607666-blue-MODEL.jpg.avif',
                'rating': 4.3,
                'reviews': 278,
                'specs': ['Slim Fit', '98% Cotton', 'Machine Wash', 'Multiple Sizes']
            },
            'P006': {
                'name': 'Canon EOS R6 Mark II',
                'price': 2499.99,
                'category': 'Electronics',
                'description': 'Full-frame mirrorless camera with 4K video recording and advanced autofocus.',
                'stock': 8,
                'image': 'assets/products/Canon_EOS_R6_Mark_II.jpeg',
                'rating': 4.6,
                'reviews': 92,
                'specs': ['Full Frame', '4K Video', 'Image Stabilization', 'Dual Card Slots']
            },
            'P007': {
                'name': 'Samsung 4K Smart TV 55"',
                'price': 799.99,
                'category': 'Electronics',
                'description': '55-inch 4K UHD Smart TV with HDR and built-in streaming apps.',
                'stock': 12,
                'image': 'assets/products/Samsung 4K Smart TV 55.jpeg',
                'rating': 4.4,
                'reviews': 167,
                'specs': ['4K UHD', 'Smart TV', 'HDR Support', '55" Display']
            },
            'P008': {
                'name': 'Adidas Ultraboost 22',
                'price': 189.99,
                'category': 'Footwear',
                'description': 'Premium running shoes with Boost midsole technology and Primeknit upper.',
                'stock': 35,
                'image': 'assets/products/Adidas Ultraboost 22.jpeg',
                'rating': 4.6,
                'reviews': 203,
                'specs': ['Boost Technology', 'Primeknit Upper', 'Continental Rubber', 'Energy Return']
            },

            # === Page 1: Home & Kitchen ===
            'P009': {
                'name': 'Keurig K-Elite Coffee Maker',
                'price': 149.99,
                'category': 'Home & Kitchen',
                'description': 'Single-serve coffee maker with iced coffee capability and a 75oz water reservoir.',
                'stock': 40,
                'image': 'assets/products/Keurig K-Elite Coffee Maker.jpeg',
                'rating': 4.7,
                'reviews': 412,
                'specs': ['Single Serve', 'Iced Coffee Setting', '75oz Reservoir', 'Strong Brew Option']
            },
            'P010': {
                'name': 'Ninja AF101 Air Fryer',
                'price': 99.99,
                'category': 'Home & Kitchen',
                'description': 'Crisp, dehydrate, and roast your favorite foods with little to no oil. 4-quart capacity.',
                'stock': 60,
                'image': 'assets/products/Ninja AF101 Air Fryer.jpeg',
                'rating': 4.8,
                'reviews': 530,
                'specs': ['4-Quart Capacity', 'Air Fry, Roast, Reheat', 'Dishwasher Safe', '1550 Watts']
            },
            'P011': {
                'name': 'Instant Pot Duo 7-in-1',
                'price': 89.99,
                'category': 'Home & Kitchen',
                'description': 'Electric pressure cooker, slow cooker, rice cooker, steamer, and more in one appliance.',
                'stock': 30,
                'image': 'assets/products/Instant Pot Duo 7-in-1.jpeg',
                'rating': 4.7,
                'reviews': 1205,
                'specs': ['7-in-1 Functionality', '6-Quart Capacity', 'Stainless Steel', '13 Smart Programs']
            },
            'P012': {
                'name': 'Dyson V11 Cordless Vacuum',
                'price': 599.99,
                'category': 'Home & Kitchen',
                'description': 'Powerful and intelligent cordless vacuum for a deep clean anywhere.',
                'stock': 15,
                'image': 'assets/products/Dyson V11 Cordless Vacuum.jpeg',
                'rating': 4.6,
                'reviews': 310,
                'specs': ['60 Min Runtime', 'LCD Screen', 'Advanced Filtration', 'Lightweight Design']
            },
            'P013': {
                'name': 'Vitamix Explorian Blender',
                'price': 349.95,
                'category': 'Home & Kitchen',
                'description': 'Professional-grade blender for smoothies, soups, and frozen desserts.',
                'stock': 22,
                'image': 'assets/products/Vitamix Explorian Blender.jpeg',
                'rating': 4.9,
                'reviews': 288,
                'specs': ['Variable Speed Control', '64-Ounce Container', 'Aircraft-Grade Blades', 'Self-Cleaning']
            },
            'P014': {
                'name': 'Amazon Echo Dot (5th Gen)',
                'price': 49.99,
                'category': 'Electronics',
                'description': 'Smart speaker with Alexa for voice control of your music, smart home, and more.',
                'stock': 100,
                'image': 'assets/products/Amazon Echo Dot (5th Gen).jpeg',
                'rating': 4.7,
                'reviews': 980,
                'specs': ['Alexa Built-in', 'Improved Audio', 'Smart Home Hub', 'Privacy Controls']
            },
            'P015': {
                'name': 'Philips Hue Starter Kit',
                'price': 129.99,
                'category': 'Home & Kitchen',
                'description': 'Smart LED light bulbs with a hub to control your lighting from your phone or voice.',
                'stock': 45,
                'image': 'assets/products/Philips Hue Starter Kit.jpeg',
                'rating': 4.5,
                'reviews': 190,
                'specs': ['2 White & Color Bulbs', 'Hue Hub Included', 'Works with Alexa/Google', '16 Million Colors']
            },
            'P016': {
                'name': 'KitchenAid Stand Mixer',
                'price': 449.99,
                'category': 'Home & Kitchen',
                'description': 'The ultimate tool for baking, with a 5-quart bowl and 10 speed settings.',
                'stock': 18,
                'image': 'assets/products/KitchenAid Stand Mixer.jpeg',
                'rating': 4.9,
                'reviews': 650,
                'specs': ['5-Quart Bowl', '10 Speeds', 'Tilt-Head Design', 'Includes 3 Attachments']
            },
            'P017': {
                'name': 'Breville Smart Oven Air Fryer',
                'price': 399.95,
                'category': 'Home & Kitchen',
                'description': 'A versatile countertop oven with 13 cooking functions including air fry and dehydrate.',
                'stock': 14,
                'image': 'assets/products/Breville Smart Oven Air Fryer.jpeg',
                'rating': 4.8,
                'reviews': 240,
                'specs': ['13-in-1 Functions', 'Convection Cooking', 'Large Capacity', 'LCD Display']
            },
            'P018': {
                'name': 'Nespresso VertuoPlus Coffee Machine',
                'price': 159.00,
                'category': 'Home & Kitchen',
                'description': 'Single-serve coffee and espresso machine using Centrifusion technology for perfect crema.',
                'stock': 33,
                'image': 'assets/products/Nespresso VertuoPlus Coffee Machine.jpeg',
                'rating': 4.6,
                'reviews': 350,
                'specs': ['Coffee & Espresso', 'Centrifusion Technology', 'Automatic Blend Recognition', 'Fast Heat-up']
            },
            'P019': {
                'name': 'Cuisinart 14-Cup Food Processor',
                'price': 249.95,
                'category': 'Home & Kitchen',
                'description': 'Powerful food processor for chopping, slicing, shredding, and mixing.',
                'stock': 25,
                'image': '🔪',
                'rating': 4.7,
                'reviews': 210,
                'specs': ['14-Cup Capacity', '720-Watt Motor', 'Stainless Steel Blades', 'Easy to Clean']
            },
            'P020': {
                'name': 'Lodge Cast Iron Skillet 12"',
                'price': 29.99,
                'category': 'Home & Kitchen',
                'description': 'Pre-seasoned and ready-to-use cast iron skillet for versatile cooking.',
                'stock': 80,
                'image': '🍳',
                'rating': 4.8,
                'reviews': 1500,
                'specs': ['12-Inch Diameter', 'Pre-Seasoned', 'Superior Heat Retention', 'Made in USA']
            },
            'P021': {
                'name': 'Simplehuman 58L Step Can',
                'price': 199.99,
                'category': 'Home & Kitchen',
                'description': 'Dual-compartment trash can for easy recycling and waste management.',
                'stock': 28,
                'image': '🗑️',
                'rating': 4.9,
                'reviews': 400,
                'specs': ['Dual Compartment', '58-Liter Capacity', 'Liner Pocket', 'Soft-close Lid']
            },
            'P022': {
                'name': 'Brooklinen Luxe Core Sheet Set',
                'price': 179.00,
                'category': 'Home & Kitchen',
                'description': 'Buttery-smooth 480 thread count sateen sheets for ultimate comfort.',
                'stock': 50,
                'image': '🛏️',
                'rating': 4.6,
                'reviews': 620,
                'specs': ['480 Thread Count', '100% Long-Staple Cotton', 'Sateen Weave', 'Queen Size']
            },
            'P023': {
                'name': 'Herman Miller Aeron Chair',
                'price': 1545.00,
                'category': 'Home & Kitchen',
                'description': 'Ergonomic office chair designed for maximum comfort and support.',
                'stock': 10,
                'image': '🪑',
                'rating': 4.9,
                'reviews': 320,
                'specs': ['Ergonomic Design', 'PostureFit SL Support', 'Adjustable Arms', 'Breathable Pellicle']
            },
            'P024': {
                'name': 'Nest Learning Thermostat',
                'price': 249.00,
                'category': 'Home & Kitchen',
                'description': 'Smart thermostat that learns your schedule and programs itself to save energy.',
                'stock': 40,
                'image': '🌡️',
                'rating': 4.7,
                'reviews': 780,
                'specs': ['Auto-Schedule', 'Energy Saving', 'Remote Control', 'Works with Alexa']
            },
            'P025': {
                'name': 'Anker PowerWave Wireless Charger',
                'price': 19.99,
                'category': 'Electronics',
                'description': 'Fast wireless charging stand for iPhone and Android devices.',
                'stock': 120,
                'image': '🔋',
                'rating': 4.5,
                'reviews': 1100,
                'specs': ['10W Fast Charging', 'Case Friendly', 'Portrait/Landscape Mode', 'Non-Slip Pad']
            },
            'P026': {
                'name': 'Ember Temperature Control Smart Mug 2',
                'price': 129.95,
                'category': 'Home & Kitchen',
                'description': 'Keeps your hot beverage at the exact temperature you prefer.',
                'stock': 35,
                'image': '☕',
                'rating': 4.4,
                'reviews': 250,
                'specs': ['1.5 Hour Battery', 'App-Controlled', 'Customizable LED', '10 oz Capacity']
            },

            # === Page 2: Sports & Outdoors ===
            'P027': {
                'name': 'Liforme Original Yoga Mat',
                'price': 140.00,
                'category': 'Sports & Outdoors',
                'description': 'Non-slip yoga mat with alignment markers for a perfect practice.',
                'stock': 55,
                'image': '🧘',
                'rating': 4.9,
                'reviews': 300,
                'specs': ['GripForMe Material', 'AlignForMe System', 'Eco-Friendly', 'Larger & Wider']
            },
            'P028': {
                'name': 'Bowflex SelectTech 552 Dumbbells',
                'price': 429.00,
                'category': 'Sports & Outdoors',
                'description': 'Adjustable dumbbells that replace 15 sets of weights. Adjust from 5 to 52.5 lbs.',
                'stock': 20,
                'image': '🏋️',
                'rating': 4.8,
                'reviews': 850,
                'specs': ['Adjustable 5-52.5 lbs', 'Rapid-Switch Dial', 'Space Efficient', 'Quiet Workouts']
            },
            'P029': {
                'name': 'Garmin Forerunner 245 Music',
                'price': 349.99,
                'category': 'Sports & Outdoors',
                'description': 'GPS running watch with music storage, advanced dynamics, and performance monitoring.',
                'stock': 30,
                'image': '⌚',
                'rating': 4.7,
                'reviews': 640,
                'specs': ['GPS Tracking', 'Music Storage', 'VO2 Max Monitoring', 'Safety Features']
            },
            'P030': {
                'name': 'The North Face Borealis Backpack',
                'price': 99.00,
                'category': 'Sports & Outdoors',
                'description': 'Versatile backpack with a padded laptop sleeve and comfortable FlexVent suspension.',
                'stock': 70,
                'image': '🎒',
                'rating': 4.6,
                'reviews': 510,
                'specs': ['28-Liter Capacity', 'FlexVent Suspension', 'Laptop Sleeve', 'Sternum Strap']
            },
            'P031': {
                'name': 'Hydro Flask Wide Mouth 32 oz',
                'price': 44.95,
                'category': 'Sports & Outdoors',
                'description': 'Insulated stainless steel water bottle that keeps drinks cold for 24 hours or hot for 12.',
                'stock': 150,
                'image': '💧',
                'rating': 4.9,
                'reviews': 2100,
                'specs': ['TempShield Insulation', 'Pro-Grade Stainless Steel', 'BPA-Free', 'Durable Powder Coat']
            },
            'P032': {
                'name': 'Patagonia Nano Puff Jacket',
                'price': 199.00,
                'category': 'Clothing',
                'description': 'Lightweight, windproof, and water-resistant jacket with PrimaLoft Gold Insulation.',
                'stock': 40,
                'image': '🧥',
                'rating': 4.8,
                'reviews': 450,
                'specs': ['PrimaLoft Gold Insulation', '100% Recycled Shell', 'Windproof', 'Water-Resistant']
            },
            'P033': {
                'name': 'Osprey Atmos AG 65 Backpacking Pack',
                'price': 270.00,
                'category': 'Sports & Outdoors',
                'description': 'Award-winning backpacking pack with Anti-Gravity suspension for incredible comfort.',
                'stock': 18,
                'image': '🎒',
                'rating': 4.9,
                'reviews': 380,
                'specs': ['Anti-Gravity Suspension', '65-Liter Capacity', 'Integrated Raincover',
                          'Trekking Pole Attachment']
            },
            'P034': {
                'name': 'Specialized Allez E5 Road Bike',
                'price': 1200.00,
                'category': 'Sports & Outdoors',
                'description': 'An entry-level road bike that offers exceptional performance and versatility.',
                'stock': 12,
                'image': '🚲',
                'rating': 4.5,
                'reviews': 120,
                'specs': ['E5 Premium Aluminum Frame', 'Shimano Claris Groupset', 'Carbon Fork', 'Axis Sport Wheels']
            },
            'P035': {
                'name': 'Coleman Sundome 4-Person Tent',
                'price': 69.99,
                'category': 'Sports & Outdoors',
                'description': 'Easy-to-set-up dome tent perfect for car camping and weekend getaways.',
                'stock': 65,
                'image': '⛺',
                'rating': 4.4,
                'reviews': 950,
                'specs': ['Sleeps 4 People', 'WeatherTec System', '10-Minute Setup', 'Large Windows']
            },
            'P036': {
                'name': 'Spalding NBA Street Basketball',
                'price': 24.99,
                'category': 'Sports & Outdoors',
                'description': 'Official size and weight basketball with a durable outdoor performance rubber cover.',
                'stock': 200,
                'image': '🏀',
                'rating': 4.6,
                'reviews': 1300,
                'specs': ['Official NBA Size 7', 'Performance Rubber Cover', 'Deep Channel Design', 'For Outdoor Play']
            },
            'P037': {
                'name': 'YETI Tundra 45 Cooler',
                'price': 299.99,
                'category': 'Sports & Outdoors',
                'description': 'Legendary cooler with PermaFrost insulation for unmatched ice retention.',
                'stock': 25,
                'image': '🧊',
                'rating': 4.9,
                'reviews': 980,
                'specs': ['FatWall Design', 'PermaFrost Insulation', 'Rotomolded Construction', 'Bear-Resistant']
            },
            'P038': {
                'name': 'Black Diamond Spot 400 Headlamp',
                'price': 49.95,
                'category': 'Sports & Outdoors',
                'description': 'A bright, waterproof headlamp with multiple modes for any outdoor adventure.',
                'stock': 90,
                'image': '🔦',
                'rating': 4.7,
                'reviews': 350,
                'specs': ['400 Lumen Output', 'IPX8 Waterproof', 'PowerTap Technology', 'Red Night-Vision Mode']
            },
            'P039': {
                'name': 'Theragun Prime Massage Gun',
                'price': 299.00,
                'category': 'Sports & Outdoors',
                'description': 'Percussive therapy device for deep muscle treatment, recovery, and pain relief.',
                'stock': 30,
                'image': '💪',
                'rating': 4.8,
                'reviews': 420,
                'specs': ['QuietForce Technology', '5 Speeds', 'App Integration', '4 Attachments']
            },
            'P040': {
                'name': 'Peloton Bike+',
                'price': 2495.00,
                'category': 'Sports & Outdoors',
                'description': 'The ultimate indoor cycling experience with a rotating screen and live classes.',
                'stock': 10,
                'image': '🚲',
                'rating': 4.7,
                'reviews': 1100,
                'specs': ['23.8" HD Rotating Screen', 'Live & On-Demand Classes', 'Auto-Resistance',
                          'Apple GymKit Integration']
            },
            'P041': {
                'name': 'Salomon Speedcross 5 Trail Runners',
                'price': 130.00,
                'category': 'Footwear',
                'description': 'Iconic trail running shoes with aggressive grip for soft, technical trails.',
                'stock': 45,
                'image': '👟',
                'rating': 4.6,
                'reviews': 390,
                'specs': ['Aggressive Grip', 'SensiFit Cradle', 'Welded Upper', 'Quicklace System']
            },
            'P042': {
                'name': 'Titleist Pro V1 Golf Balls',
                'price': 54.99,
                'category': 'Sports & Outdoors',
                'description': 'The number one ball in golf, offering total performance for every player.',
                'stock': 100,
                'image': '⛳',
                'rating': 4.9,
                'reviews': 720,
                'specs': ['12-Ball Pack', 'Soft Feel', 'Long Distance', 'Drop-and-Stop Control']
            },
            'P043': {
                'name': 'Wilson Blade 98 Tennis Racket',
                'price': 249.00,
                'category': 'Sports & Outdoors',
                'description': 'A popular racket choice for its feel, stability, and connected-to-the-ball experience.',
                'stock': 28,
                'image': '🎾',
                'rating': 4.7,
                'reviews': 180,
                'specs': ['98 sq. in. Head Size', 'FORTYFIVE° Technology', 'DirectConnect Carbon',
                          'For Advanced Players']
            },
            'P044': {
                'name': 'GoPro HERO11 Black',
                'price': 499.99,
                'category': 'Electronics',
                'description': 'The latest action camera with a larger sensor, improved stabilization, and incredible image quality.',
                'stock': 22,
                'image': '📹',
                'rating': 4.6,
                'reviews': 290,
                'specs': ['5.3K60 Video', 'HyperSmooth 5.0', 'Waterproof to 33ft', 'Large Image Sensor']
            },

            # === Page 3: Health & Beauty ===
            'P045': {
                'name': 'Philips Sonicare DiamondClean Toothbrush',
                'price': 199.95,
                'category': 'Health & Beauty',
                'description': 'Removes up to 10x more plaque for healthier gums in just two weeks.',
                'stock': 40,
                'image': '🪥',
                'rating': 4.8,
                'reviews': 880,
                'specs': ['5 Brushing Modes', 'Pressure Sensor', 'Charging Glass', 'Travel Case']
            },
            'P046': {
                'name': 'Dyson Supersonic Hair Dryer',
                'price': 429.99,
                'category': 'Health & Beauty',
                'description': 'Engineered to protect hair from extreme heat damage, with fast drying and controlled styling.',
                'stock': 15,
                'image': '💨',
                'rating': 4.7,
                'reviews': 650,
                'specs': ['Intelligent Heat Control', 'Powerful Digital Motor', 'Magnetic Attachments',
                          'Acoustically Tuned']
            },
            'P047': {
                'name': 'The Ordinary - The Balance Set',
                'price': 29.00,
                'category': 'Health & Beauty',
                'description': 'A skincare regimen to target textural irregularities, dullness, and signs of congestion.',
                'stock': 120,
                'image': '🧴',
                'rating': 4.5,
                'reviews': 1200,
                'specs': ['4-Piece Set', 'Targets Blemishes', 'Vegan & Cruelty-Free', 'For Oily Skin']
            },
            'P048': {
                'name': 'Fitbit Charge 5',
                'price': 149.95,
                'category': 'Health & Beauty',
                'description': 'Advanced fitness & health tracker with built-in GPS, stress management tools and sleep tracking.',
                'stock': 60,
                'image': '💓',
                'rating': 4.4,
                'reviews': 950,
                'specs': ['Built-in GPS', 'EDA & ECG Sensors', 'Color Touchscreen', '7-Day Battery Life']
            },
            'P049': {
                'name': 'Kiehl\'s Ultra Facial Cream',
                'price': 34.00,
                'category': 'Health & Beauty',
                'description': 'A 24-hour daily moisturizer that leaves skin feeling soft, smooth, and hydrated.',
                'stock': 85,
                'image': '💧',
                'rating': 4.8,
                'reviews': 780,
                'specs': ['24-Hour Hydration', 'For All Skin Types', 'Lightweight Texture', 'With Glacial Glycoprotein']
            },
            'P050': {
                'name': 'Dior Sauvage Eau de Toilette',
                'price': 104.00,
                'category': 'Health & Beauty',
                'description': 'A radically fresh composition, dictated by a name that has the ring of a manifesto.',
                'stock': 50,
                'image': '✨',
                'rating': 4.7,
                'reviews': 1500,
                'specs': ['3.4 oz Bottle', 'Fresh & Woody Scent', 'Notes of Bergamot', 'Long-Lasting']
            },
            'P051': {
                'name': 'Aesop Resurrection Aromatique Hand Wash',
                'price': 40.00,
                'category': 'Health & Beauty',
                'description': 'A gentle formulation containing oils of Orange, Rosemary, and Lavender to effectively cleanse the hands.',
                'stock': 70,
                'image': '🧼',
                'rating': 4.9,
                'reviews': 600,
                'specs': ['16.9 oz Bottle', 'Botanical Ingredients', 'Gentle on Skin', 'Aromatic Scent']
            },
            'P052': {
                'name': 'Braun Series 9 Pro Electric Shaver',
                'price': 329.94,
                'category': 'Health & Beauty',
                'description': 'The world’s most efficient electric shaver, designed for a flawless close shave.',
                'stock': 25,
                'image': '🧔',
                'rating': 4.6,
                'reviews': 410,
                'specs': ['Wet & Dry Use', 'ProLift Trimmer', '40,000 Cutting Actions', 'Clean&Charge Station']
            },
            'P053': {
                'name': 'GHD Platinum+ Styler',
                'price': 279.00,
                'category': 'Health & Beauty',
                'description': 'A smart hair straightener that predicts your hair\'s needs for ultimate results.',
                'stock': 30,
                'image': '💈',
                'rating': 4.8,
                'reviews': 320,
                'specs': ['Predictive Technology', 'Optimal 365°F Temperature', 'Wishbone Hinge', 'Universal Voltage']
            },
            'P054': {
                'name': 'Crest 3D Whitestrips',
                'price': 45.99,
                'category': 'Health & Beauty',
                'description': 'Professional-level teeth whitening results at home, removing 14 years of stains.',
                'stock': 90,
                'image': '😁',
                'rating': 4.5,
                'reviews': 2500,
                'specs': ['20 Treatments', 'Advanced Seal Technology', 'Enamel Safe', 'Noticeable Results in 3 Days']
            },
            'P055': {
                'name': 'Supergoop! Unseen Sunscreen SPF 40',
                'price': 36.00,
                'category': 'Health & Beauty',
                'description': 'An invisible, weightless, and scentless sunscreen that acts as a makeup-gripping primer.',
                'stock': 110,
                'image': '☀️',
                'rating': 4.7,
                'reviews': 1800,
                'specs': ['SPF 40 Protection', 'Broad Spectrum', 'Oil-Free', 'Reef-Safe']
            },
            'P056': {
                'name': 'Waterpik Aquarius Water Flosser',
                'price': 79.99,
                'category': 'Health & Beauty',
                'description': 'Removes up to 99.9% of plaque from treated areas and is 50% more effective than string floss.',
                'stock': 55,
                'image': '💦',
                'rating': 4.6,
                'reviews': 1250,
                'specs': ['10 Pressure Settings', '7 Tips Included', '90-Second Water Capacity',
                          'Massage Mode for Gums']
            },
            'P057': {
                'name': 'Olaplex No. 3 Hair Perfector',
                'price': 30.00,
                'category': 'Health & Beauty',
                'description': 'An at-home treatment that reduces breakage and visibly strengthens hair.',
                'stock': 150,
                'image': '💆',
                'rating': 4.8,
                'reviews': 3500,
                'specs': ['Repairs Damaged Hair', 'Strengthens Bonds', 'For All Hair Types', 'Use Before Shampooing']
            },
            'P058': {
                'name': 'Slip Pure Silk Pillowcase',
                'price': 89.00,
                'category': 'Health & Beauty',
                'description': 'Anti-aging, anti-sleep crease, and anti-bed head pillowcase made from pure mulberry silk.',
                'stock': 60,
                'image': '😴',
                'rating': 4.9,
                'reviews': 980,
                'specs': ['100% Mulberry Silk', 'Anti-Aging Benefits', 'Gentle on Hair & Skin', 'Queen Size']
            },
            'P059': {
                'name': 'NARS Radiant Creamy Concealer',
                'price': 31.00,
                'category': 'Health & Beauty',
                'description': 'An award-winning concealer that provides medium-to-full, buildable coverage.',
                'stock': 100,
                'image': '💄',
                'rating': 4.7,
                'reviews': 2200,
                'specs': ['16-Hour Wear', 'Corrects & Contours', 'Light-Diffusing Technology', '30 Shades Available']
            },
            'P060': {
                'name': 'Lush Bath Bomb - Intergalactic',
                'price': 8.95,
                'category': 'Health & Beauty',
                'description': 'A mix of peppermint and neon color sends your mood rocketing, while popping candy takes you on a trip through the Milky Way.',
                'stock': 200,
                'image': '💣',
                'rating': 4.9,
                'reviews': 1500,
                'specs': ['Vegan', 'Peppermint Scent', 'Popping Candy', 'Handmade']
            },
            'P061': {
                'name': 'La Mer Crème de la Mer',
                'price': 380.00,
                'category': 'Health & Beauty',
                'description': 'An ultra-rich cream that instantly immerses skin in healing moisture and reveals a firmer feel.',
                'stock': 12,
                'image': '💎',
                'rating': 4.6,
                'reviews': 450,
                'specs': ['50ml Jar', 'Miracle Broth™', 'Ultra-Rich Texture', 'Soothes Dryness']
            },
            'P062': {
                'name': 'Withings Body+ Smart Scale',
                'price': 99.95,
                'category': 'Health & Beauty',
                'description': 'A Wi-Fi body composition smart scale that tracks weight, BMI, body fat, and more.',
                'stock': 40,
                'image': '⚖️',
                'rating': 4.5,
                'reviews': 750,
                'specs': ['Full Body Composition', 'Wi-Fi & Bluetooth Sync', 'Multi-User Friendly',
                          'Pregnancy & Baby Mode']
            },

            # === Page 4: Books, Movies & Games ===
            'P063': {
                'name': 'Atomic Habits by James Clear',
                'price': 14.99,
                'category': 'Books',
                'description': 'A proven framework for improving every day by making tiny, easy changes.',
                'stock': 150,
                'image': '📚',
                'rating': 4.9,
                'reviews': 5500,
                'specs': ['Hardcover', '320 Pages', 'Self-Help', 'New York Times Bestseller']
            },
            'P064': {
                'name': 'Dune by Frank Herbert',
                'price': 10.99,
                'category': 'Books',
                'description': 'The classic science fiction masterpiece, a stunning blend of adventure and mysticism.',
                'stock': 120,
                'image': '📖',
                'rating': 4.8,
                'reviews': 3200,
                'specs': ['Paperback', '896 Pages', 'Science Fiction', 'Hugo Award Winner']
            },
            'P065': {
                'name': 'Nintendo Switch - OLED Model',
                'price': 349.99,
                'category': 'Electronics',
                'description': 'Features a vibrant 7-inch OLED screen, a wide adjustable stand, and 64 GB of internal storage.',
                'stock': 35,
                'image': '🎮',
                'rating': 4.8,
                'reviews': 1200,
                'specs': ['7-Inch OLED Screen', '64 GB Storage', 'Enhanced Audio', '3 Play Modes']
            },
            'P066': {
                'name': 'The Midnight Library by Matt Haig',
                'price': 15.60,
                'category': 'Books',
                'description': 'A novel about all the choices that go into a life well-lived.',
                'stock': 90,
                'image': '📚',
                'rating': 4.6,
                'reviews': 2800,
                'specs': ['Hardcover', '304 Pages', 'Contemporary Fiction', 'Goodreads Choice Winner']
            },
            'P067': {
                'name': 'Sony PlayStation 5 Console',
                'price': 499.99,
                'category': 'Electronics',
                'description': 'Experience lightning-fast loading with an ultra-high-speed SSD and deeper immersion with haptic feedback.',
                'stock': 10,
                'image': '🎮',
                'rating': 4.9,
                'reviews': 2500,
                'specs': ['Ultra-High-Speed SSD', 'Haptic Feedback', '4K-TV Gaming', 'Ray Tracing']
            },
            'P068': {
                'name': 'The Lord of the Rings Trilogy (4K Blu-ray)',
                'price': 89.99,
                'category': 'Movies',
                'description': 'The complete cinematic trilogy, remastered in stunning 4K Ultra HD.',
                'stock': 40,
                'image': '🎬',
                'rating': 4.9,
                'reviews': 1800,
                'specs': ['4K Ultra HD', '9-Disc Set', 'Theatrical & Extended', 'Dolby Atmos']
            },
            'P069': {
                'name': 'Kindle Paperwhite',
                'price': 139.99,
                'category': 'Electronics',
                'description': 'Now with a 6.8” display and thinner borders, adjustable warm light, and up to 10 weeks of battery life.',
                'stock': 75,
                'image': '📖',
                'rating': 4.7,
                'reviews': 4500,
                'specs': ['6.8" Glare-Free Display', 'Waterproof (IPX8)', 'Adjustable Warm Light',
                          'Weeks of Battery Life']
            },
            'P070': {
                'name': 'Elden Ring - PlayStation 5',
                'price': 59.99,
                'category': 'Games',
                'description': 'A new fantasy action RPG. Rise, Tarnished, and be guided by grace to brandish the power of the Elden Ring.',
                'stock': 60,
                'image': '⚔️',
                'rating': 4.9,
                'reviews': 1500,
                'specs': ['Action RPG', 'Vast Open World', 'FromSoftware', 'Game of the Year']
            },
            'P071': {
                'name': 'The Psychology of Money by Morgan Housel',
                'price': 17.99,
                'category': 'Books',
                'description': 'Timeless lessons on wealth, greed, and happiness.',
                'stock': 110,
                'image': '💰',
                'rating': 4.7,
                'reviews': 2100,
                'specs': ['Paperback', '256 Pages', 'Personal Finance', 'Bestseller']
            },
            'P072': {
                'name': 'Codenames Board Game',
                'price': 19.95,
                'category': 'Games',
                'description': 'A social word game with a simple premise and challenging gameplay for two rival spymasters.',
                'stock': 130,
                'image': '🎲',
                'rating': 4.8,
                'reviews': 3500,
                'specs': ['4-8+ Players', '15 Min Playtime', 'Ages 10+', 'Party Game']
            },
            'P073': {
                'name': 'Xbox Series X Console',
                'price': 499.99,
                'category': 'Electronics',
                'description': 'The fastest, most powerful Xbox ever. Explore rich new worlds with 12 teraflops of raw graphic processing power.',
                'stock': 15,
                'image': '🎮',
                'rating': 4.8,
                'reviews': 1900,
                'specs': ['12 Teraflops Power', '1TB Custom SSD', '4K Gaming at 120 FPS', 'Quick Resume']
            },
            'P074': {
                'name': 'Where the Crawdads Sing by Delia Owens',
                'price': 9.99,
                'category': 'Books',
                'description': 'A heartbreaking coming-of-age story and a surprising tale of possible murder.',
                'stock': 200,
                'image': '📖',
                'rating': 4.7,
                'reviews': 6000,
                'specs': ['Paperback', '384 Pages', 'Mystery Fiction', '#1 Bestseller']
            },
            'P075': {
                'name': 'Spider-Man: Across the Spider-Verse (Blu-ray)',
                'price': 24.99,
                'category': 'Movies',
                'description': 'Miles Morales catapults across the Multiverse, where he encounters a team of Spider-People.',
                'stock': 80,
                'image': '🕷️',
                'rating': 4.9,
                'reviews': 1100,
                'specs': ['Blu-ray + Digital', 'Animated Feature', 'Action/Adventure', 'Oscar Nominee']
            },
            'P076': {
                'name': 'The Legend of Zelda: Tears of the Kingdom',
                'price': 69.99,
                'category': 'Games',
                'description': 'An epic adventure across the land and skies of Hyrule awaits in the sequel to Breath of the Wild.',
                'stock': 50,
                'image': '🛡️',
                'rating': 5.0,
                'reviews': 2200,
                'specs': ['Nintendo Switch', 'Action-Adventure', 'Open World', 'Sequel to BOTW']
            },
            'P077': {
                'name': 'Sapiens: A Brief History of Humankind',
                'price': 18.50,
                'category': 'Books',
                'description': 'A groundbreaking narrative of humanity’s creation and evolution.',
                'stock': 95,
                'image': '🧠',
                'rating': 4.8,
                'reviews': 4100,
                'specs': ['Paperback', '464 Pages', 'Non-Fiction', 'History']
            },
            'P078': {
                'name': 'Settlers of Catan Board Game',
                'price': 43.99,
                'category': 'Games',
                'description': 'The classic strategy game of trading and building. Guide your settlers to victory.',
                'stock': 85,
                'image': '🎲',
                'rating': 4.7,
                'reviews': 2800,
                'specs': ['3-4 Players', '60 Min Playtime', 'Ages 10+', 'Strategy Game']
            },
            'P079': {
                'name': 'Harry Potter Paperback Box Set',
                'price': 59.99,
                'category': 'Books',
                'description': 'The complete 7-book collection of the magical Harry Potter series.',
                'stock': 70,
                'image': '⚡',
                'rating': 4.9,
                'reviews': 7500,
                'specs': ['7 Books', 'Paperback', 'Fantasy', 'Complete Series']
            },
            'P080': {
                'name': 'Cyberpunk 2077: Ultimate Edition',
                'price': 59.99,
                'category': 'Games',
                'description': 'The complete Cyberpunk experience, including the Phantom Liberty expansion.',
                'stock': 45,
                'image': '🤖',
                'rating': 4.5,
                'reviews': 900,
                'specs': ['PS5/Xbox Series X', 'Action RPG', 'Open World', 'Includes Expansion']
            },

            # === Page 5: More Clothing & Accessories ===
            'P081': {
                'name': 'Ray-Ban Classic Aviator Sunglasses',
                'price': 163.00,
                'category': 'Accessories',
                'description': 'Timeless model that combines great aviator styling with exceptional quality, performance, and comfort.',
                'stock': 60,
                'image': '🕶️',
                'rating': 4.7,
                'reviews': 950,
                'specs': ['100% UV Protection', 'Metal Frame', 'G-15 Green Lenses', 'Made in Italy']
            },
            'P082': {
                'name': 'Fjällräven Kånken Classic Backpack',
                'price': 80.00,
                'category': 'Accessories',
                'description': 'A classic backpack made from hard-wearing Vinylon F fabric with a zip that opens the entire main compartment.',
                'stock': 90,
                'image': '🎒',
                'rating': 4.8,
                'reviews': 1200,
                'specs': ['16-Liter Capacity', 'Vinylon F Fabric', 'Water-Resistant', 'Removable Seat Pad']
            },
            'P083': {
                'name': 'Seiko 5 Sports Automatic Watch',
                'price': 275.00,
                'category': 'Accessories',
                'description': 'A reliable and stylish automatic watch with a day-date display and durable construction.',
                'stock': 30,
                'image': '⌚',
                'rating': 4.6,
                'reviews': 620,
                'specs': ['Automatic Movement', 'Stainless Steel Case', '100m Water Resistance', 'Day-Date Display']
            },
            'P084': {
                'name': 'Allbirds Wool Runners',
                'price': 110.00,
                'category': 'Footwear',
                'description': 'Soft, cozy, and breathable sneakers made from ZQ Merino wool.',
                'stock': 70,
                'image': '👟',
                'rating': 4.5,
                'reviews': 1800,
                'specs': ['ZQ Merino Wool Upper', 'Machine Washable', 'Carbon Neutral', 'Cushioned Midsole']
            },
            'P085': {
                'name': 'Carhartt Acrylic Watch Hat A18',
                'price': 19.99,
                'category': 'Accessories',
                'description': 'A classic, warm, and stretchable rib-knit hat that is a staple for cold weather.',
                'stock': 250,
                'image': '🧢',
                'rating': 4.9,
                'reviews': 4500,
                'specs': ['100% Acrylic', 'Rib-Knit Fabric', 'One Size Fits All', 'Carhartt Label']
            },
            'P086': {
                'name': 'Lululemon ABC Pant Classic',
                'price': 128.00,
                'category': 'Clothing',
                'description': 'Pants designed for all-day comfort and versatility, from work to the weekend.',
                'stock': 55,
                'image': '👖',
                'rating': 4.7,
                'reviews': 980,
                'specs': ['Warpstreme™ Fabric', 'Four-Way Stretch', 'Wrinkle-Resistant', 'Hidden Pockets']
            },
            'P087': {
                'name': 'Gucci GG Marmont Leather Belt',
                'price': 490.00,
                'category': 'Accessories',
                'description': 'A slim leather belt with the iconic Double G buckle.',
                'stock': 20,
                'image': '🎗️',
                'rating': 4.8,
                'reviews': 350,
                'specs': ['Black Leather', 'Antique Brass Hardware', 'Double G Buckle', 'Made in Italy']
            },
            'P088': {
                'name': 'Birkenstock Arizona Sandals',
                'price': 110.00,
                'category': 'Footwear',
                'description': 'A comfort legend and a fashion staple with its two-strap design and cork footbed.',
                'stock': 80,
                'image': '👡',
                'rating': 4.6,
                'reviews': 2100,
                'specs': ['Suede Upper', 'Contoured Cork Footbed', 'EVA Sole', 'Adjustable Straps']
            },
            'P089': {
                'name': 'Champion Reverse Weave Hoodie',
                'price': 60.00,
                'category': 'Clothing',
                'description': 'The original heavyweight hoodie known for its durability and comfort.',
                'stock': 100,
                'image': '👕',
                'rating': 4.7,
                'reviews': 1500,
                'specs': ['Heavyweight Fleece', 'Athletic Fit', 'Double-Needle Construction', 'Signature Rib Panels']
            },
            'P090': {
                'name': 'The Ridge Wallet',
                'price': 95.00,
                'category': 'Accessories',
                'description': 'A minimalist, RFID-blocking wallet that holds 1-12 cards without stretching out.',
                'stock': 65,
                'image': '💳',
                'rating': 4.9,
                'reviews': 1300,
                'specs': ['Aluminum/Titanium', 'RFID Blocking', 'Holds 1-12 Cards', 'Integrated Money Clip']
            },
            'P091': {
                'name': 'UGG Classic Short II Boot',
                'price': 170.00,
                'category': 'Footwear',
                'description': 'Iconic sheepskin boot that is pretreated to protect against moisture and staining.',
                'stock': 40,
                'image': '👢',
                'rating': 4.5,
                'reviews': 1100,
                'specs': ['Twinface Sheepskin', 'Treadlite by UGG™ Sole', 'Pretreated for Water Resistance',
                          '8" Shaft Height']
            },
            'P092': {
                'name': 'Brooks Brothers Oxford Cloth Shirt',
                'price': 140.00,
                'category': 'Clothing',
                'description': 'The original Polo button-down Oxford shirt, an icon of American style.',
                'stock': 50,
                'image': '👔',
                'rating': 4.6,
                'reviews': 480,
                'specs': ['Supima Cotton', 'Button-Down Collar', 'Classic Fit', 'Signature 6-Pleat Shirring']
            },
            'P093': {
                'name': 'Away The Carry-On',
                'price': 275.00,
                'category': 'Accessories',
                'description': 'Thoughtfully designed carry-on luggage with a durable polycarbonate shell and 360° spinner wheels.',
                'stock': 35,
                'image': '🧳',
                'rating': 4.8,
                'reviews': 850,
                'specs': ['Polycarbonate Shell', '360° Spinner Wheels', 'Interior Compression', 'TSA-Approved Lock']
            },
            'P094': {
                'name': 'Dr. Martens 1460 Smooth Leather Boots',
                'price': 170.00,
                'category': 'Footwear',
                'description': 'The original Dr. Martens boot, instantly recognizable with its 8 eyes and yellow stitching.',
                'stock': 45,
                'image': '🥾',
                'rating': 4.7,
                'reviews': 1900,
                'specs': ['Goodyear Welted', 'Air-Cushioned Sole', 'Durable Smooth Leather', '8-Eye Design']
            },
            'P095': {
                'name': 'Smartwool Hiking Socks',
                'price': 24.00,
                'category': 'Clothing',
                'description': 'Performance hiking socks made with Merino wool for comfort, breathability, and durability.',
                'stock': 180,
                'image': '🧦',
                'rating': 4.9,
                'reviews': 2200,
                'specs': ['Merino Wool Blend', 'Performance Fit', 'Medium Cushion', 'Virtually Seamless™ Toe']
            },
            'P096': {
                'name': 'Apple Watch Series 9',
                'price': 399.00,
                'category': 'Electronics',
                'description': 'The ultimate device for a healthy life with a new S9 chip, a brighter display, and Double Tap gesture.',
                'stock': 40,
                'image': '⌚',
                'rating': 4.8,
                'reviews': 950,
                'specs': ['S9 SiP Chip', 'Double Tap Gesture', 'Brighter Display', 'Advanced Health Sensors']
            },
            'P097': {
                'name': 'Everlane The Cashmere Crew',
                'price': 145.00,
                'category': 'Clothing',
                'description': 'A classic crewneck sweater made from soft, Grade-A Mongolian cashmere.',
                'stock': 60,
                'image': '👕',
                'rating': 4.6,
                'reviews': 680,
                'specs': ['100% Grade-A Cashmere', 'Classic Fit', 'Soft & Lightweight', 'Ethically Sourced']
            },
            'P098': {
                'name': 'Canada Goose Expedition Parka',
                'price': 1495.00,
                'category': 'Clothing',
                'description': 'The original extreme weather parka, developed for scientists working in Antarctica.',
                'stock': 10,
                'image': '🧥',
                'rating': 4.9,
                'reviews': 400,
                'specs': ['Rated for -30°C & Below', '625 Fill Power Down', 'Arctic Tech® Fabric', 'Coyote Fur Ruff']
            },
        }

    # Initialize other session state variables
    if 'cart' not in st.session_state:
        st.session_state.cart = {}

    if 'orders' not in st.session_state:
        st.session_state.orders = {}

    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

    if 'page' not in st.session_state:
        st.session_state.page = 'home'


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user(email: str, password: str) -> bool:
    if email in st.session_state.users:
        return st.session_state.users[email]['password'] == hash_password(password)
    return False


def register_user(email: str, password: str, name: str) -> bool:
    if email not in st.session_state.users:
        st.session_state.users[email] = {
            'password': hash_password(password),
            'name': name,
            'created_at': datetime.now(),
            'is_admin': email == 'admin@techmart.com'
        }
        return True
    return False


def add_to_cart(product_id: str, quantity: int = 1):
    if st.session_state.current_user:
        user_cart_key = f"{st.session_state.current_user}_cart"
        if user_cart_key not in st.session_state:
            st.session_state[user_cart_key] = {}

        if product_id in st.session_state[user_cart_key]:
            st.session_state[user_cart_key][product_id] += quantity
        else:
            st.session_state[user_cart_key][product_id] = quantity


def get_user_cart():
    if st.session_state.current_user:
        user_cart_key = f"{st.session_state.current_user}_cart"
        return st.session_state.get(user_cart_key, {})
    return {}


def calculate_cart_total():
    cart = get_user_cart()
    total = 0
    for product_id, quantity in cart.items():
        if product_id in st.session_state.products:
            total += st.session_state.products[product_id]['price'] * quantity
    return total


def create_order():
    if not st.session_state.current_user:
        return None

    cart = get_user_cart()
    if not cart:
        return None

    order_id = str(uuid.uuid4())[:8]
    order = {
        'id': order_id,
        'user': st.session_state.current_user,
        'items': cart.copy(),
        'total': calculate_cart_total(),
        'status': 'Pending',
        'created_at': datetime.now(),
        'estimated_delivery': datetime.now() + timedelta(days=7)
    }

    # Update stock
    for product_id, quantity in cart.items():
        if product_id in st.session_state.products:
            st.session_state.products[product_id]['stock'] -= quantity

    # Save order
    st.session_state.orders[order_id] = order

    # Clear cart
    user_cart_key = f"{st.session_state.current_user}_cart"
    st.session_state[user_cart_key] = {}

    return order_id


# =============================================================================
# HEADER WITH BRANDING
# =============================================================================

def render_header():
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; text-align: center; margin: 0;">
            🛒 TechMart - Premium Online Store
        </h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0;">
            Your one-stop shop for electronics, fashion, and more!
        </p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# AUTHENTICATION SYSTEM
# =============================================================================

def render_auth():
    st.sidebar.markdown("### 🔐 Account")

    if st.session_state.current_user:
        user_info = st.session_state.users[st.session_state.current_user]
        st.sidebar.success(f"Welcome, {user_info['name']}!")

        if st.sidebar.button("🚪 Logout"):
            st.session_state.current_user = None
            st.rerun()
    else:
        tab1, tab2 = st.sidebar.tabs(["Login", "Register"])

        with tab1:
            with st.form("login_form"):
                email = st.text_input("📧 Email")
                password = st.text_input("🔒 Password", type="password")

                if st.form_submit_button("Login"):
                    if authenticate_user(email, password):
                        st.session_state.current_user = email
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials!")

        with tab2:
            with st.form("register_form"):
                name = st.text_input("👤 Full Name")
                email = st.text_input("📧 Email")
                password = st.text_input("🔒 Password", type="password")
                confirm_password = st.text_input("🔒 Confirm Password", type="password")

                if st.form_submit_button("Register"):
                    if password != confirm_password:
                        st.error("Passwords don't match!")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters!")
                    elif register_user(email, password, name):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Email already exists!")


# =============================================================================
# PRODUCT DISPLAY WITH IMAGES
# =============================================================================

def render_product_card(product_id: str, product: Dict):
    """
    Render individual product card with image support

    IMAGE CUSTOMIZATION:
    - Change the width/height in get_image_html() call
    - Modify the CSS classes for different styling
    - Add hover effects or animations as needed
    """
    with st.container():
        st.markdown(f"""
        <div class="product-card">
            <div class="product-image-container">
                {get_image_html(product['image'], width="100%", height="200px")}
            </div>
            <h3 style="margin: 1rem 0 0.5rem 0; color: #333;">{product['name']}</h3>
            <p style="font-size: 1.5rem; font-weight: bold; color: #667eea; margin: 0.5rem 0;">
                ${product['price']:.2f}
            </p>
            <p style="color: #666; margin: 0.5rem 0;">{product['description']}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;">
                <span>⭐ {product['rating']}/5 ({product['reviews']} reviews)</span>
                <span style="color: {'#28a745' if product['stock'] > 10 else '#dc3545' if product['stock'] > 0 else '#6c757d'};">
                    📦 {product['stock']} in stock
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Product specifications
        if 'specs' in product:
            with st.expander("📋 Specifications"):
                for spec in product['specs']:
                    st.write(f"• {spec}")

        # Add to cart section
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            quantity = st.number_input(
                "Qty",
                min_value=1,
                max_value=min(10, product['stock']),
                value=1,
                key=f"qty_{product_id}"
            )

        with col2:
            if st.button("🛒 Add to Cart", key=f"cart_{product_id}"):
                if st.session_state.current_user:
                    if product['stock'] >= quantity:
                        add_to_cart(product_id, quantity)
                        st.success(f"Added {quantity} item(s) to cart!")
                        st.rerun()
                    else:
                        st.error("Not enough stock!")
                else:
                    st.warning("Please login to add items to cart!")

        with col3:
            if st.button("👁️ Quick View", key=f"view_{product_id}"):
                st.session_state.selected_product = product_id
                st.session_state.show_product_modal = True


# =============================================================================
# HOME PAGE WITH PRODUCT CATALOG
# =============================================================================

def render_home():
    st.markdown("## 🏠 Featured Products")

    # Search and filter section
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_term = st.text_input("🔍 Search products", placeholder="Search for products...")
    with col2:
        category_filter = st.selectbox(
            "📂 Category",
            ["All"] + list(set(p['category'] for p in st.session_state.products.values()))
        )
    with col3:
        sort_by = st.selectbox("🔄 Sort by", ["Name", "Price (Low to High)", "Price (High to Low)", "Rating"])

    # Filter products
    filtered_products = {}
    for pid, product in st.session_state.products.items():
        # Search filter
        if (search_term.lower() in product['name'].lower() or
                search_term.lower() in product['description'].lower() or
                search_term == ""):
            # Category filter
            if category_filter == "All" or product['category'] == category_filter:
                filtered_products[pid] = product

    # Sort products
    if sort_by == "Name":
        filtered_products = dict(sorted(filtered_products.items(), key=lambda x: x[1]['name']))
    elif sort_by == "Price (Low to High)":
        filtered_products = dict(sorted(filtered_products.items(), key=lambda x: x[1]['price']))
    elif sort_by == "Price (High to Low)":
        filtered_products = dict(sorted(filtered_products.items(), key=lambda x: x[1]['price'], reverse=True))
    elif sort_by == "Rating":
        filtered_products = dict(sorted(filtered_products.items(), key=lambda x: x[1]['rating'], reverse=True))

    # Display products
    if filtered_products:
        # Show results count
        st.markdown(f"*Showing {len(filtered_products)} products*")

        # Create responsive product grid
        cols = st.columns(3)
        for idx, (product_id, product) in enumerate(filtered_products.items()):
            with cols[idx % 3]:
                render_product_card(product_id, product)
    else:
        st.info("🔍 No products found matching your search criteria.")
        st.markdown("### 💡 Suggestions:")
        st.markdown("- Try different keywords")
        st.markdown("- Check your spelling")
        st.markdown("- Browse all categories")


# =============================================================================
# SHOPPING CART WITH PRODUCT IMAGES
# =============================================================================

def render_cart():
    st.markdown("## 🛒 Shopping Cart")

    if not st.session_state.current_user:
        st.warning("Please login to view your cart.")
        return

    cart = get_user_cart()

    if not cart:
        st.info("Your cart is empty. Start shopping!")
        if st.button("🛍️ Browse Products"):
            st.session_state.page = 'home'
            st.rerun()
        return

    total = 0

    # Cart items with images
    for product_id, quantity in cart.items():
        if product_id in st.session_state.products:
            product = st.session_state.products[product_id]
            subtotal = product['price'] * quantity
            total += subtotal

            st.markdown(f"""
            <div class="cart-item">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div>
                        {get_image_html(product['image'], width="80px", height="80px")}
                    </div>
                    <div style="flex-grow: 1;">
                        <h4 style="margin: 0; color: #333;">{product['name']}</h4>
                        <p style="margin: 0.5rem 0; color: #666;">
                            Quantity: {quantity} × ${product['price']:.2f}
                        </p>
                        <p style="margin: 0; font-size: 0.9rem; color: #888;">
                            {product['category']} • In Stock: {product['stock']}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <h4 style="margin: 0; color: #667eea;">${subtotal:.2f}</h4>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 2])
            with col1:
                if st.button("🗑️ Remove", key=f"remove_{product_id}"):
                    user_cart_key = f"{st.session_state.current_user}_cart"
                    del st.session_state[user_cart_key][product_id]
                    st.rerun()

            # Option to update quantity
            with col2:
                new_qty = st.number_input(
                    "Update Qty",
                    min_value=1,
                    max_value=product['stock'],
                    value=quantity,
                    key=f"update_qty_{product_id}"
                )
                if new_qty != quantity:
                    if st.button("Update", key=f"update_{product_id}"):
                        user_cart_key = f"{st.session_state.current_user}_cart"
                        st.session_state[user_cart_key][product_id] = new_qty
                        st.rerun()

    # Cart summary
    st.markdown("---")
    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #667eea;">
            <h3 style="margin: 0; color: #333;">Cart Summary</h3>
            <p style="margin: 0.5rem 0;">Items: {sum(cart.values())}</p>
            <h2 style="margin: 0.5rem 0; color: #667eea;">Total: ${total:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    # Action buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🛍️ Continue Shopping", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()

    with col2:
        if st.button("💳 Checkout", use_container_width=True, type="primary"):
            order_id = create_order()
            if order_id:
                st.session_state.page = 'orders'
                st.success(f"🎉 Order #{order_id} placed successfully!")
                st.balloons()
                st.rerun()


# =============================================================================
# ORDER MANAGEMENT
# =============================================================================

def render_orders():
    st.markdown("## 📋 My Orders")

    if not st.session_state.current_user:
        st.warning("Please login to view your orders.")
        return

    user_orders = {
        oid: order for oid, order in st.session_state.orders.items()
        if order['user'] == st.session_state.current_user
    }

    if not user_orders:
        st.info("You haven't placed any orders yet.")
        if st.button("🛍️ Start Shopping"):
            st.session_state.page = 'home'
            st.rerun()
        return

    # Order statistics
    total_spent = sum(order['total'] for order in user_orders.values())
    total_items = sum(sum(order['items'].values()) for order in user_orders.values())

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Orders", len(user_orders))
    with col2:
        st.metric("Total Items", total_items)
    with col3:
        st.metric("Total Spent", f"${total_spent:.2f}")

    # Display orders
    for order_id, order in sorted(user_orders.items(), key=lambda x: x[1]['created_at'], reverse=True):
        status_color = {
            'Pending': '#ffc107',
            'Processing': '#17a2b8',
            'Shipped': '#fd7e14',
            'Delivered': '#28a745',
            'Cancelled': '#dc3545'
        }

        with st.expander(f"📦 Order #{order_id} - ${order['total']:.2f} ({order['status']})"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Order Date:** {order['created_at'].strftime('%B %d, %Y at %I:%M %p')}")
                st.write(f"**Estimated Delivery:** {order['estimated_delivery'].strftime('%B %d, %Y')}")

                # Order status with color
                st.markdown(f"""
                <div style="display: inline-block; background: {status_color.get(order['status'], '#6c757d')}; 
                           color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem;">
                    {order['status']}
                </div>
                """, unsafe_allow_html=True)

                st.write("**Items Ordered:**")
                for product_id, quantity in order['items'].items():
                    if product_id in st.session_state.products:
                        product = st.session_state.products[product_id]
                        item_total = product['price'] * quantity

                        st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 1rem; margin: 0.5rem 0; 
                                   padding: 0.5rem; background: #f8f9fa; border-radius: 8px;">
                            <div>
                                {get_image_html(product['image'], width="50px", height="50px")}
                            </div>
                            <div style="flex-grow: 1;">
                                <strong>{product['name']}</strong><br>
                                <small>{quantity} × ${product['price']:.2f} = ${item_total:.2f}</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            with col2:
                # Order tracking visual
                st.markdown("**Order Progress:**")
                statuses = ['Pending', 'Processing', 'Shipped', 'Delivered']
                current_index = statuses.index(order['status']) if order['status'] in statuses else 0

                for i, status in enumerate(statuses):
                    if i <= current_index:
                        st.markdown(f"✅ {status}")
                    else:
                        st.markdown(f"⭕ {status}")

                # Reorder button
                if st.button("🔄 Reorder Items", key=f"reorder_{order_id}"):
                    if st.session_state.current_user:
                        user_cart_key = f"{st.session_state.current_user}_cart"
                        if user_cart_key not in st.session_state:
                            st.session_state[user_cart_key] = {}

                        for product_id, quantity in order['items'].items():
                            if product_id in st.session_state.products:
                                if product_id in st.session_state[user_cart_key]:
                                    st.session_state[user_cart_key][product_id] += quantity
                                else:
                                    st.session_state[user_cart_key][product_id] = quantity

                        st.success("Items added to cart!")
                        st.rerun()


# =============================================================================
# ADMIN PANEL WITH IMAGE MANAGEMENT
# =============================================================================

def render_admin():
    """
    Admin panel with comprehensive management features

    IMAGE MANAGEMENT FEATURES:
    - Upload new product images
    - Preview existing images
    - Update product images
    - Bulk image operations
    """
    if not st.session_state.current_user or not st.session_state.users.get(st.session_state.current_user, {}).get(
            'is_admin'):
        st.error("🚫 Access denied. Admin privileges required.")
        return

    st.markdown("## ⚙️ Admin Dashboard")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "📦 Products", "📋 Orders", "👥 Users"])

    with tab1:
        # Analytics Dashboard
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{len(st.session_state.products)}</h3>
                <p>Total Products</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{len(st.session_state.orders)}</h3>
                <p>Total Orders</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            total_revenue = sum(order['total'] for order in st.session_state.orders.values())
            st.markdown(f"""
            <div class="metric-card">
                <h3>${total_revenue:.2f}</h3>
                <p>Total Revenue</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            total_users = len(st.session_state.users)
            st.markdown(f"""
            <div class="metric-card">
                <h3>{total_users}</h3>
                <p>Registered Users</p>
            </div>
            """, unsafe_allow_html=True)

        # Charts and Analytics
        if st.session_state.orders:
            col1, col2 = st.columns(2)

            with col1:
                # Revenue over time
                order_data = []
                for order in st.session_state.orders.values():
                    order_data.append({
                        'date': order['created_at'].date(),
                        'revenue': order['total']
                    })

                df = pd.DataFrame(order_data)
                if not df.empty:
                    daily_revenue = df.groupby('date')['revenue'].sum().reset_index()
                    fig = px.line(daily_revenue, x='date', y='revenue',
                                  title='📈 Daily Revenue Trend')
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Category distribution
                category_data = {}
                for product in st.session_state.products.values():
                    category_data[product['category']] = category_data.get(product['category'], 0) + 1

                fig2 = px.pie(
                    values=list(category_data.values()),
                    names=list(category_data.keys()),
                    title='🍰 Products by Category'
                )
                st.plotly_chart(fig2, use_container_width=True)

            # Top products
            st.markdown("### 🏆 Top Selling Products")
            product_sales = {}
            for order in st.session_state.orders.values():
                for product_id, quantity in order['items'].items():
                    product_sales[product_id] = product_sales.get(product_id, 0) + quantity

            if product_sales:
                top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
                for product_id, sales in top_products:
                    if product_id in st.session_state.products:
                        product = st.session_state.products[product_id]
                        col1, col2, col3 = st.columns([1, 3, 1])
                        with col1:
                            st.markdown(get_image_html(product['image'], width="50px", height="50px"),
                                        unsafe_allow_html=True)
                        with col2:
                            st.write(f"**{product['name']}**")
                            st.write(f"{product['category']} • ${product['price']:.2f}")
                        with col3:
                            st.metric("Sold", sales)

    with tab2:
        # Product Management with Image Support
        st.markdown("### ➕ Add New Product")

        with st.form("add_product"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Product Name *")
                price = st.number_input("Price ($) *", min_value=0.01, step=0.01)
                category = st.selectbox("Category *",
                                        ["Electronics", "Clothing", "Footwear", "Home", "Sports", "Books", "Other"])
                stock = st.number_input("Initial Stock *", min_value=0, step=1)

            with col2:
                description = st.text_area("Product Description *")

                # Image input options
                image_option = st.radio("Image Type:", ["Emoji/Icon", "Upload Image", "Image URL"])

                if image_option == "Emoji/Icon":
                    image_input = st.text_input("Emoji/Icon", value="📦",
                                                help="Enter an emoji or icon to represent the product")
                elif image_option == "Upload Image":
                    uploaded_file = st.file_uploader("Upload Product Image",
                                                     type=['png', 'jpg', 'jpeg', 'gif', 'webp'])
                    image_input = uploaded_file
                else:  # Image URL
                    image_input = st.text_input("Image URL",
                                                placeholder="https://example.com/image.jpg")

                # Product specifications
                specs_input = st.text_area("Specifications (one per line)",
                                           placeholder="Enter product specs, one per line")

            if st.form_submit_button("➕ Add Product", type="primary"):
                if name and price and category and description:
                    product_id = f"P{len(st.session_state.products) + 1:03d}"

                    # Handle image
                    if image_option == "Upload Image" and uploaded_file is not None:
                        image_path = save_uploaded_image(uploaded_file, product_id)
                        final_image = image_path if image_path else "📦"
                    else:
                        final_image = image_input if image_input else "📦"

                    # Handle specifications
                    specs = [spec.strip() for spec in specs_input.split('\n') if spec.strip()] if specs_input else []

                    # Create product
                    st.session_state.products[product_id] = {
                        'name': name,
                        'price': price,
                        'category': category,
                        'description': description,
                        'stock': stock,
                        'image': final_image,
                        'rating': 4.0,
                        'reviews': 0,
                        'specs': specs
                    }
                    st.success(f"✅ Product '{name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields marked with *")

        st.markdown("---")
        st.markdown("### 📦 Current Products")

        # Product management table
        for pid, product in st.session_state.products.items():
            with st.expander(f"{product['name']} - ${product['price']:.2f} (Stock: {product['stock']})"):
                col1, col2, col3 = st.columns([1, 2, 1])

                with col1:
                    st.markdown("**Current Image:**")
                    st.markdown(get_image_html(product['image'], width="120px", height="120px"),
                                unsafe_allow_html=True)

                with col2:
                    st.write(f"**ID:** {pid}")
                    st.write(f"**Category:** {product['category']}")
                    st.write(f"**Rating:** {product['rating']}/5 ({product['reviews']} reviews)")
                    st.write(f"**Description:** {product['description']}")
                    if 'specs' in product and product['specs']:
                        st.write("**Specifications:**")
                        for spec in product['specs']:
                            st.write(f"• {spec}")

                with col3:
                    # Update stock
                    new_stock = st.number_input("Update Stock",
                                                value=product['stock'], min_value=0, key=f"stock_{pid}")
                    if st.button("Update Stock", key=f"update_stock_{pid}"):
                        st.session_state.products[pid]['stock'] = new_stock
                        st.success("Stock updated!")
                        st.rerun()

                    # Update image
                    new_image_option = st.radio(f"Update Image:",
                                                ["Keep Current", "New Emoji", "Upload New", "New URL"],
                                                key=f"img_option_{pid}")

                    if new_image_option == "New Emoji":
                        new_emoji = st.text_input("New Emoji", key=f"emoji_{pid}")
                        if st.button("Update Image", key=f"update_img_{pid}") and new_emoji:
                            st.session_state.products[pid]['image'] = new_emoji
                            st.success("Image updated!")
                            st.rerun()

                    elif new_image_option == "Upload New":
                        new_upload = st.file_uploader("New Image",
                                                      type=['png', 'jpg', 'jpeg', 'gif'], key=f"upload_{pid}")
                        if st.button("Update Image", key=f"update_img_{pid}") and new_upload:
                            new_path = save_uploaded_image(new_upload, pid)
                            if new_path:
                                st.session_state.products[pid]['image'] = new_path
                                st.success("Image updated!")
                                st.rerun()

                    elif new_image_option == "New URL":
                        new_url = st.text_input("New URL", key=f"url_{pid}")
                        if st.button("Update Image", key=f"update_img_{pid}") and new_url:
                            st.session_state.products[pid]['image'] = new_url
                            st.success("Image updated!")
                            st.rerun()

                    # Delete product
                    if st.button("🗑️ Delete Product", key=f"del_{pid}", type="secondary"):
                        del st.session_state.products[pid]
                        st.success("Product deleted!")
                        st.rerun()

    with tab3:
        # Order Management
        st.markdown("### 📋 Order Management")

        if st.session_state.orders:
            # Order statistics
            status_counts = {}
            for order in st.session_state.orders.values():
                status = order['status']
                status_counts[status] = status_counts.get(status, 0) + 1

            col1, col2, col3, col4 = st.columns(4)
            for i, (status, count) in enumerate(status_counts.items()):
                with [col1, col2, col3, col4][i % 4]:
                    st.metric(status, count)

            # Orders table
            for order_id, order in sorted(st.session_state.orders.items(),
                                          key=lambda x: x[1]['created_at'], reverse=True):
                with st.expander(f"Order #{order_id} - {order['user']} - ${order['total']:.2f} ({order['status']})"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.write(f"**Date:** {order['created_at'].strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Customer:** {order['user']}")
                        st.write(f"**Total Amount:** ${order['total']:.2f}")
                        st.write(f"**Estimated Delivery:** {order['estimated_delivery'].strftime('%Y-%m-%d')}")

                        st.write("**Items Ordered:**")
                        for pid, qty in order['items'].items():
                            if pid in st.session_state.products:
                                product = st.session_state.products[pid]
                                st.markdown(f"""
                                <div style="display: flex; align-items: center; gap: 0.5rem; margin: 0.25rem 0;">
                                    {get_image_html(product['image'], width="30px", height="30px")}
                                    <span>{product['name']} × {qty} = ${product['price'] * qty:.2f}</span>
                                </div>
                                """, unsafe_allow_html=True)

                    with col2:
                        # Update order status
                        current_status = order['status']
                        new_status = st.selectbox(
                            "Order Status",
                            ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"],
                            index=["Pending", "Processing", "Shipped", "Delivered", "Cancelled"].index(current_status),
                            key=f"status_{order_id}"
                        )

                        if st.button("💾 Update Status", key=f"update_{order_id}"):
                            st.session_state.orders[order_id]['status'] = new_status
                            st.success(f"Order #{order_id} status updated to {new_status}!")
                            st.rerun()

                        # Order actions
                        if st.button("📧 Send Update Email", key=f"email_{order_id}"):
                            st.info("Email notification sent! (Demo mode)")

                        if current_status in ["Pending", "Processing"] and st.button("❌ Cancel Order",
                                                                                     key=f"cancel_{order_id}"):
                            # Restore stock
                            for pid, qty in order['items'].items():
                                if pid in st.session_state.products:
                                    st.session_state.products[pid]['stock'] += qty

                            st.session_state.orders[order_id]['status'] = 'Cancelled'
                            st.success("Order cancelled and stock restored!")
                            st.rerun()
        else:
            st.info("📦 No orders placed yet.")

    with tab4:
        # User Management
        st.markdown("### 👥 User Management")

        if st.session_state.users:
            user_data = []
            for email, user in st.session_state.users.items():
                # Calculate user stats
                user_orders = [o for o in st.session_state.orders.values() if o['user'] == email]
                total_spent = sum(o['total'] for o in user_orders)

                user_data.append({
                    'Email': email,
                    'Name': user['name'],
                    'Admin': '✅' if user.get('is_admin', False) else '❌',
                    'Registered': user['created_at'].strftime('%Y-%m-%d'),
                    'Orders': len(user_orders),
                    'Total Spent': f"${total_spent:.2f}"
                })

            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True)

            # User actions
            st.markdown("### 🔧 User Actions")
            selected_user = st.selectbox("Select User", list(st.session_state.users.keys()))

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("👑 Make Admin"):
                    st.session_state.users[selected_user]['is_admin'] = True
                    st.success(f"{selected_user} is now an admin!")
                    st.rerun()

            with col2:
                if st.button("👤 Remove Admin"):
                    if selected_user != 'admin@techmart.com':  # Protect main admin
                        st.session_state.users[selected_user]['is_admin'] = False
                        st.success(f"Admin privileges removed from {selected_user}")
                        st.rerun()
                    else:
                        st.error("Cannot remove admin privileges from main admin!")

            with col3:
                if st.button("📊 View User Details"):
                    user = st.session_state.users[selected_user]
                    user_orders = [o for o in st.session_state.orders.values() if o['user'] == selected_user]

                    st.write(f"**Name:** {user['name']}")
                    st.write(f"**Email:** {selected_user}")
                    st.write(f"**Registered:** {user['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Total Orders:** {len(user_orders)}")
                    st.write(f"**Total Spent:** ${sum(o['total'] for o in user_orders):.2f}")
        else:
            st.info("👤 No users registered yet.")


# =============================================================================
# NAVIGATION SIDEBAR
# =============================================================================

def render_navigation():
    st.sidebar.markdown("### 🧭 Navigation")

    pages = {
        '🏠 Home': 'home',
        '🛒 Cart': 'cart',
        '📋 My Orders': 'orders'
    }

    # Add admin page for admin users
    if (st.session_state.current_user and
            st.session_state.users.get(st.session_state.current_user, {}).get('is_admin')):
        pages['⚙️ Admin'] = 'admin'

    # Show cart item count
    cart_count = len(get_user_cart())
    cart_label = '🛒 Cart'
    if cart_count > 0:
        cart_label = f'🛒 Cart ({cart_count})'
        pages[cart_label] = 'cart'
        del pages['🛒 Cart']  # Remove the old key

    for page_name, page_key in pages.items():
        if st.sidebar.button(page_name, use_container_width=True):
            st.session_state.page = page_key
            st.rerun()


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """
    Main application entry point

    CUSTOMIZATION NOTES:
    1. To add your own images, modify the products dictionary in init_session_state()
    2. Create an 'assets' folder structure for local images
    3. Update the CSS classes for different styling
    4. Add more product categories or features as needed
    """
    init_session_state()
    render_header()
    render_auth()
    render_navigation()

    # Quick stats and cart summary in sidebar
    if st.session_state.current_user:
        cart_total = calculate_cart_total()
        cart_count = len(get_user_cart())

        if cart_total > 0:
            st.sidebar.markdown(f"""
            <div style="background: linear-gradient(135deg, #28a745, #20c997); 
                       color: white; padding: 1rem; border-radius: 12px; margin: 1rem 0;
                       box-shadow: 0 4px 12px rgba(40,167,69,0.3);">
                <h4 style="margin: 0; text-align: center;">🛒 Cart Summary</h4>
                <div style="text-align: center; margin: 0.5rem 0;">
                    <div style="font-size: 1.2rem;">{cart_count} items</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">${cart_total:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Quick actions
        st.sidebar.markdown("### ⚡ Quick Actions")
        if st.sidebar.button("🛍️ View Cart", use_container_width=True):
            st.session_state.page = 'cart'
            st.rerun()

        if cart_total > 0:
            if st.sidebar.button("💳 Quick Checkout", use_container_width=True, type="primary"):
                order_id = create_order()
                if order_id:
                    st.session_state.page = 'orders'
                    st.success(f"🎉 Order #{order_id} placed successfully!")
                    st.balloons()
                    st.rerun()

    # Current page rendering
    if st.session_state.page == 'home':
        render_home()
    elif st.session_state.page == 'cart':
        render_cart()
    elif st.session_state.page == 'orders':
        render_orders()
    elif st.session_state.page == 'admin':
        render_admin()

    # Footer with image credits and instructions
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem; background: #f8f9fa; border-radius: 12px;">
        <h4>🛒 TechMart © 2024 | Built with Streamlit</h4>
        <p><strong>Demo Credentials:</strong> admin@techmart.com / admin123</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()