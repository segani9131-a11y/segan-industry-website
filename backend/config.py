"""
Configuration loader for Segan Industry API.
Loads settings from config.json and provides them as a Python module.
"""

import json
import os
from typing import Dict, Any
from pathlib import Path

# Get the directory of this file
CONFIG_DIR = Path(__file__).parent
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file."""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load configuration
config = load_config()

# Export commonly used configs for easy access
company = config["company"]
gst = config["gst"]
gst_rates = config["gst_rates"]
suppliers = config["suppliers"]
materials = config["materials"]
machinery = config["machinery"]
employees = config["employees"]
production = config["production"]
inventory = config["inventory"]
quotation = config["quotation"]
email = config["email"]
database = config["database"]
ai_agent = config["ai_agent"]

def get_material_price(material_name: str) -> Dict[str, Any]:
    """Get material price configuration."""
    return config["materials"].get(material_name, {})

def get_supplier_by_id(supplier_id: str) -> Dict[str, Any]:
    """Get supplier details by ID."""
    for sup in suppliers:
        if sup["id"] == supplier_id:
            return sup
    return {}

def get_suppliers_for_material(material_type: str) -> list:
    """Get all suppliers for a specific material type."""
    return [s for s in suppliers if material_type in s.get("materials", [])]

def get_machinery_by_id(machine_id: str) -> Dict[str, Any]:
    """Get machinery details by ID."""
    for m in machinery:
        if m["id"] == machine_id:
            return m
    return {}

def get_gst_rate(product_category: str) -> int:
    """Get GST rate for a product category."""
    return gst_rates.get(product_category, 18)

def is_interstate_gst(state_code: str) -> bool:
    """Check if transaction is inter-state (different from Tamil Nadu state code 33)."""
    return state_code != "33"

# Reload function for development
def reload_config():
    """Reload configuration from file."""
    global config, company, gst, gst_rates, suppliers, materials, machinery
    global employees, production, inventory, quotation, email, database, ai_agent
    config = load_config()
    company = config["company"]
    gst = config["gst"]
    gst_rates = config["gst_rates"]
    suppliers = config["suppliers"]
    materials = config["materials"]
    machinery = config["machinery"]
    employees = config["employees"]
    production = config["production"]
    inventory = config["inventory"]
    quotation = config["quotation"]
    email = config["email"]
    database = config["database"]
    ai_agent = config["ai_agent"]