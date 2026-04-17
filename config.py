import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
PROFILES_DIR = BASE_DIR / "profiles"

# --- Culling thresholds ---
SHARPNESS_MIN = 80.0          # Laplacian variance — below = blurry reject
NOISE_MAX = 45.0              # Noise variance — above = noisy reject
EXPOSURE_LOW = 30             # Mean brightness — below = underexposed
EXPOSURE_HIGH = 225           # Mean brightness — above = overexposed
DUPLICATE_THRESHOLD = 10      # pHash hamming distance — below = duplicate
BLINK_RATIO_MIN = 0.20        # Eye aspect ratio — below = eyes closed
EXPRESSION_MIN_SCORE = 0.30   # DeepFace confidence — below = bad expression
HEAD_POSE_YAW_MAX = 40        # Degrees — above = not looking at camera
MOTION_BLUR_THRESHOLD = 5     # FFT high-freq ratio — below = motion blur

# --- Editing defaults ---
WB_ALGORITHM = "gray_world"   # gray_world | white_patch
NOISE_STRENGTH = 10           # fastNlMeans filter strength (3-21)
SHARPEN_AMOUNT = 1.5          # Unsharp mask amount
SHARPEN_RADIUS = 1.0          # Unsharp mask radius
UPSCALE_FACTOR = 2            # Real-ESRGAN scale (2x or 4x)
VIGNETTE_STRENGTH = 0.4       # 0.0 = none, 1.0 = heavy
BOKEH_BLUR_RADIUS = 21        # Portrait background blur kernel size

# --- Retouching defaults ---
SKIN_SMOOTH_DIAMETER = 9      # Bilateral filter diameter
SKIN_SMOOTH_SIGMA = 75        # Bilateral filter sigma
BLEMISH_MASK_RADIUS = 12      # Inpainting radius around detected spots
SHINE_THRESHOLD = 230         # Highlight value — above = oily/shiny
EYE_BRIGHTEN_AMOUNT = 30      # HSV value boost for eyes
TEETH_WHITEN_AMOUNT = 40      # HSV saturation reduce for teeth
DARK_CIRCLE_BRIGHTEN = 25     # HSV value boost under eyes

# --- Pipeline mode ---
GPU_ENABLED = True            # Auto-detected at runtime
BATCH_WORKERS = 4             # Parallel workers for CPU pipeline
OUTPUT_FORMAT = "JPEG"        # JPEG | TIFF | PNG
OUTPUT_QUALITY = 95           # JPEG quality 1-100
XMP_EXPORT = True             # Write XMP sidecar files

# --- Pricing tiers (for UI/reporting) ---
TIER_PRO_MONTHLY_PHOTOS = 3000
TIER_PRO_PRICE_EUR = 49
TIER_UNLIMITED_PRICE_EUR = 99

# --- Languages ---
SUPPORTED_LANGUAGES = ["en", "de", "hr", "bs", "sr"]
DEFAULT_LANGUAGE = "en"

MODELS_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)
