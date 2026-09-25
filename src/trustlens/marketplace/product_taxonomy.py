"""
TrustLens Marketplace Intelligence — Product Taxonomy & Enums (Phase B).
"""

from enum import Enum


class ProductDomain(str, Enum):
    ELECTRONICS = "Electronics"
    GAMING = "Gaming"
    VEHICLES = "Vehicles"
    CAMERAS = "Cameras"
    RENTAL = "Rental"
    OTHER = "Other"
    UNKNOWN = "Unknown"


class ProductCategory(str, Enum):
    SMARTPHONE = "Smartphone"
    LAPTOP = "Laptop"
    APPLE_DESKTOP = "Apple Desktop"
    GAMING_CONSOLE = "Gaming Console"
    GAMING_ACCESSORY = "Gaming Accessory"
    CAMERA = "Camera"
    VEHICLE = "Vehicle"
    AUDIO = "Audio"
    WEARABLE = "Wearable"
    ACCESSORY = "Accessory"
    OTHER = "Other"
    UNKNOWN = "Unknown"


class QueryMatchStatus(str, Enum):
    DIRECT_MATCH = "direct_match"
    RELATED_ACCESSORY = "related_accessory"
    DIFFERENT_PRODUCT = "different_product"
    AMBIGUOUS = "ambiguous"
    UNKNOWN = "unknown"


class NormalizationConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class Condition(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    USED = "used"
    REFURBISHED = "refurbished"
    FOR_PARTS = "for_parts"
    UNKNOWN = "unknown"


class AccessoryOrDevice(str, Enum):
    DEVICE = "device"
    ACCESSORY = "accessory"
    PART = "part"
    CASE = "case"
    CHARGER = "charger"
    CABLE = "cable"
    COVER = "cover"
    SCREEN_PROTECTOR = "screen_protector"
    UNKNOWN = "unknown"
