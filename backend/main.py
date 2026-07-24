from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import List, Optional
from datetime import datetime
import uuid
import json
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config, company as company_config
from models import (
    QuotationRequest, QuotationResponse, QuotationStatus,
    ProductCatalogItem, AutomationService,
    ContactRequest, ContactResponse,
    AgentRequest, AgentResponse,
    SupplierComparisonRequest, MaterialPriceComparison,
    ProfitLossCalculation, EmployeeCostCalculation,
    MachineryRecommendation, InventoryStatus,
    ProductionWorkflow, HarnessType
)
from agent import get_ai_agent, WiringHarnessAIAgent

# Initialize FastAPI app
app = FastAPI(
    title="Segan Industry API",
    description="Wiring Harness Manufacturing & Automation API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Agent
ai_agent: WiringHarnessAIAgent = get_ai_agent()

# In-memory storage (replace with database in production)
quotations_db = {}
contacts_db = {}

# ==================== HEALTH CHECK ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "company": config["company"]["name"]
    }

# ==================== QUOTATION ENDPOINTS ====================

@app.post("/api/quote", response_model=QuotationResponse, tags=["Quotation"])
async def generate_quotation(request: QuotationRequest):
    """
    Generate a wiring harness quotation with full GST breakdown.
    
    Calculates:
    - Material costs (copper wire, PVC wire, connectors, terminals, accessories)
    - Labor costs based on harness type and complexity
    - Overhead (15%) and Contingency (5%)
    - Profit margin (18%)
    - GST (CGST 9% + SGST 9% for Tamil Nadu, IGST 18% for inter-state)
    """
    try:
        quotation = ai_agent.generate_quotation(request)
        quotations_db[quotation.quotation_id] = quotation.dict()
        return quotation
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quotation generation failed: {str(e)}")


@app.get("/api/quote/{quotation_id}", response_model=QuotationResponse, tags=["Quotation"])
async def get_quotation(quotation_id: str):
    """Retrieve a quotation by ID"""
    if quotation_id not in quotations_db:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotations_db[quotation_id]


@app.get("/api/quotes", response_model=List[QuotationResponse], tags=["Quotation"])
async def list_quotations(
    status: Optional[QuotationStatus] = None,
    limit: int = 50,
    offset: int = 0
):
    """List all quotations with optional filtering"""
    quotes = list(quotations_db.values())
    if status:
        quotes = [q for q in quotes if q.get("status") == status.value]
    return quotes[offset:offset+limit]


@app.put("/api/quote/{quotation_id}/status", tags=["Quotation"])
async def update_quotation_status(quotation_id: str, status: QuotationStatus):
    """Update quotation status"""
    if quotation_id not in quotations_db:
        raise HTTPException(status_code=404, detail="Quotation not found")
    quotations_db[quotation_id]["status"] = status.value
    quotations_db[quotation_id]["updated_at"] = datetime.now().isoformat()
    return {"success": True, "quotation_id": quotation_id, "status": status.value}

# ==================== PRODUCT CATALOG ENDPOINTS ====================

@app.get("/api/products", response_model=List[ProductCatalogItem], tags=["Products"])
async def get_products(category: Optional[str] = None):
    """Get product catalog - wiring harness types, connectors, EV harness, industrial harness"""
    
    products = [
        ProductCatalogItem(
            id="PRD001",
            name="Automotive Wiring Harness - 2 Wheeler",
            description="Complete wiring harness for motorcycles and scooters including main harness, sub-harnesses, and lighting circuits",
            category="Automotive",
            specifications={
                "voltage": "12V DC",
                "wire_gauge_range": "0.5 - 2.5 mm²",
                "connector_types": ["Molex", "Yazaki", "Sumitomo", "JST"],
                "temperature_rating": "-40°C to +125°C",
                "ip_rating": "IP67",
                "standards": ["ISO 6722", "JASO D611", "AIS-029"]
            },
            applications=["Motorcycles", "Scooters", "Three-wheelers"],
            certifications=["AIS-029", "ISO 9001", "IATF 16949 (in progress)"],
            min_order_quantity=50,
            lead_time_days=21,
            base_price_range="₹800 - ₹2,500 per set"
        ),
        ProductCatalogItem(
            id="PRD002",
            name="Automotive Wiring Harness - 4 Wheeler",
            description="Full vehicle wiring harness for passenger cars including engine, body, chassis, and infotainment harnesses",
            category="Automotive",
            specifications={
                "voltage": "12V DC",
                "wire_gauge_range": "0.35 - 6.0 mm²",
                "connector_types": ["USCAR", "FAKRA", "HSD", "MQS", "GT"],
                "temperature_rating": "-40°C to +150°C",
                "ip_rating": "IP6K9K",
                "standards": ["ISO 6722", "LV 112", "LV 214", "USCAR-2"]
            },
            applications=["Passenger Cars", "SUVs", "Light Commercial Vehicles"],
            certifications=["IATF 16949", "ISO 9001", "ISO 14001", "LV 112"],
            min_order_quantity=100,
            lead_time_days=35,
            base_price_range="₹15,000 - ₹85,000 per set"
        ),
        ProductCatalogItem(
            id="PRD003",
            name="EV High Voltage Wiring Harness",
            description="High voltage (400V-800V) wiring harness for electric vehicles including battery pack, motor controller, and charging system harnesses",
            category="EV",
            specifications={
                "voltage": "400V - 800V DC",
                "wire_gauge_range": "2.5 - 50 mm²",
                "connector_types": ["HVIL", "HV Connector", "MSD", "CCS2", "GB/T", "CHAdeMO"],
                "temperature_rating": "-40°C to +150°C",
                "ip_rating": "IP6K9K / IP67",
                "standards": ["ISO 6722-1", "ISO 19642", "LV 215", "AK-LV-42", "IEC 62196"]
            },
            applications=["Electric Cars", "Electric Buses", "Electric Trucks", "Hybrid Vehicles"],
            certifications=["IATF 16949", "ISO 6469", "ISO 17409", "AIS-156"],
            min_order_quantity=20,
            lead_time_days=45,
            base_price_range="₹25,000 - ₹2,50,000 per set"
        ),
        ProductCatalogItem(
            id="PRD004",
            name="EV Low Voltage Signal Harness",
            description="Low voltage (12V/24V) signal and communication harness for EV battery management, motor control, and vehicle systems",
            category="EV",
            specifications={
                "voltage": "12V / 24V DC",
                "wire_gauge_range": "0.35 - 1.5 mm²",
                "connector_types": ["MQS", "GT", "USCAR", "D-Sub", "RJ45", "FAKRA"],
                "temperature_rating": "-40°C to +125°C",
                "ip_rating": "IP67",
                "standards": ["ISO 6722", "CAN FD", "FlexRay", "Ethernet 100/1000BASE-T1"]
            },
            applications=["BMS Harness", "Motor Controller Harness", "VCU Harness", "Charging Communication"],
            certifications=["IATF 16949", "ISO 11898", "ISO 17458"],
            min_order_quantity=50,
            lead_time_days=28,
            base_price_range="₹3,000 - ₹15,000 per set"
        ),
        ProductCatalogItem(
            id="PRD005",
            name="Industrial Control Panel Harness",
            description="Pre-assembled wiring harnesses for industrial control panels, PLC cabinets, and automation equipment",
            category="Industrial",
            specifications={
                "voltage": "24V DC / 230V AC",
                "wire_gauge_range": "0.5 - 6.0 mm²",
                "connector_types": ["Ferrules", "Terminal Blocks", "D-Sub", "M12", "RJ45", "Harting"],
                "temperature_rating": "-25°C to +80°C",
                "ip_rating": "IP20 / IP65",
                "standards": ["IEC 60204", "UL 508A", "NFPA 79", "EN 60947"]
            },
            applications=["PLC Panels", "VFD Panels", "Motor Control Centers", "Building Automation"],
            certifications=["UL 508A", "CE", "ISO 9001"],
            min_order_quantity=10,
            lead_time_days=14,
            base_price_range="₹2,000 - ₹25,000 per panel"
        ),
        ProductCatalogItem(
            id="PRD006",
            name="Industrial Machine Harness",
            description="Custom wiring harnesses for industrial machinery including CNC machines, robots, conveyors, and packaging equipment",
            category="Industrial",
            specifications={
                "voltage": "24V DC / 415V AC",
                "wire_gauge_range": "0.5 - 16 mm²",
                "connector_types": ["M12", "M23", "Harting Han", "Intercontec", "TE Industrial"],
                "temperature_rating": "-25°C to +90°C",
                "ip_rating": "IP67 / IP69K",
                "standards": ["IEC 60204", "ISO 13849", "EN 61076"]
            },
            applications=["CNC Machines", "Industrial Robots", "Conveyor Systems", "Packaging Machines"],
            certifications=["CE", "UL Listed", "ISO 9001"],
            min_order_quantity=5,
            lead_time_days=21,
            base_price_range="₹5,000 - ₹50,000 per machine"
        ),
        ProductCatalogItem(
            id="PRD007",
            name="Automotive Connectors & Terminals",
            description="Wide range of automotive-grade connectors and terminals from leading manufacturers",
            category="Components",
            specifications={
                "brands": ["Molex", "TE Connectivity", "Yazaki", "Sumitomo", "JAE", "JST", "Amphenol", "Hirose"],
                "types": ["Wire-to-Wire", "Wire-to-Board", "Board-to-Board", "FPC/FFC", "Coaxial", "High Voltage"],
                "pitch_range": "1.0mm - 6.3mm",
                "current_rating": "3A - 100A+",
                "standards": ["USCAR", "LV 214", "JASO", "ISO 8092"]
            },
            applications=["All Automotive Harnesses", "EV Harnesses", "Sensor Connections"],
            certifications=["IATF 16949", "RoHS", "REACH"],
            min_order_quantity=100,
            lead_time_days=7,
            base_price_range="₹5 - ₹500 per piece"
        ),
        ProductCatalogItem(
            id="PRD008",
            name="Custom Wiring Harness Solutions",
            description="Fully customized wiring harness design and manufacturing for specialized applications",
            category="Custom",
            specifications={
                "design_support": "Schematic capture, BOM optimization, 3D routing",
                "prototyping": "Rapid prototyping (2-3 weeks)",
                "testing": "Continuity, Hipot, Insulation Resistance, Pull Test, Environmental",
                "documentation": "As-built drawings, test reports, traceability matrix",
                "volume": "Low to High Volume"
            },
            applications=["Medical Devices", "Defense/Aerospace", "Railways", "Marine", "Special Purpose Vehicles"],
            certifications=["ISO 9001", "AS9100 (on request)", "ISO 13485 (on request)"],
            min_order_quantity=1,
            lead_time_days=30,
            base_price_range="Project-based pricing"
        )
    ]
    
    if category:
        products = [p for p in products if p.category.lower() == category.lower()]
    
    return products


@app.get("/api/products/{product_id}", response_model=ProductCatalogItem, tags=["Products"])
async def get_product(product_id: str):
    """Get specific product details"""
    products = await get_products()
    for product in products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/api/products/categories/list", tags=["Products"])
async def get_product_categories():
    """Get list of product categories"""
    products = await get_products()
    categories = list(set(p.category for p in products))
    return {"categories": sorted(categories)}

# ==================== AUTOMATION ENDPOINTS ====================

@app.get("/api/automation", response_model=List[AutomationService], tags=["Automation"])
async def get_automation_services():
    """Get automation services offered by Segan Industry"""
    services_data = ai_agent._get_automation_services()
    return [AutomationService(**svc) for svc in services_data]


@app.get("/api/automation/{service_id}", response_model=AutomationService, tags=["Automation"])
async def get_automation_service(service_id: str):
    """Get specific automation service details"""
    services = await get_automation_services()
    for svc in services:
        if svc.id == service_id:
            return svc
    raise HTTPException(status_code=404, detail="Service not found")

# ==================== CONTACT ENDPOINTS ====================

@app.post("/api/contact", response_model=ContactResponse, tags=["Contact"])
async def submit_contact(request: ContactRequest, background_tasks: BackgroundTasks):
    """
    Submit customer inquiry/contact form.
    Sends email notification and stores in database.
    """
    try:
        # Generate reference ID
        reference_id = f"SI-CT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        
        # Store in database
        contact_record = {
            "reference_id": reference_id,
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "company": request.company,
            "contact_type": request.contact_type.value,
            "subject": request.subject,
            "message": request.message,
            "status": "new",
            "created_at": datetime.now().isoformat()
        }
        contacts_db[reference_id] = contact_record
        
        # Send email notification (background task)
        background_tasks.add_task(send_contact_email, contact_record)
        
        return ContactResponse(
            success=True,
            message="Thank you for your inquiry! We will respond within 24 hours.",
            reference_id=reference_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit contact form: {str(e)}")


async def send_contact_email(contact: dict):
    """Background task to send email notification"""
    # In production, implement actual email sending using config.email settings
    print(f"[EMAIL] EMAIL SENT: New contact inquiry from {contact['name']} ({contact['email']})")
    print(f"   Subject: {contact['subject']}")
    print(f"   Type: {contact['contact_type']}")
    print(f"   Ref: {contact['reference_id']}")


@app.get("/api/contacts", tags=["Contact"])
async def list_contacts(status: Optional[str] = None, limit: int = 50):
    """List contact inquiries (admin only in production)"""
    contacts = list(contacts_db.values())
    if status:
        contacts = [c for c in contacts if c.get("status") == status]
    return contacts[-limit:]

# ==================== AI AGENT ENDPOINTS ====================

@app.post("/api/agent", response_model=AgentResponse, tags=["AI Agent"])
async def chat_with_agent(request: AgentRequest):
    """
    Chat with the Segan Industry AI Agent.
    
    Capabilities:
    - Quotation generation
    - Material price comparison
    - Profit & loss calculation
    - GST calculation (Tamil Nadu)
    - Employee welfare & cost calculation
    - Production workflow automation
    - Machinery recommendation
    - Inventory tracking
    - Supplier selection
    - Company information
    """
    try:
        response = ai_agent.process_message(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Agent error: {str(e)}")


@app.get("/api/agent/help", tags=["AI Agent"])
async def get_agent_help():
    """Get AI agent help and capabilities"""
    return {"help": ai_agent._get_help_message()}


@app.get("/api/agent/sessions/{session_id}", tags=["AI Agent"])
async def get_session_history(session_id: str):
    """Get conversation history for a session"""
    if session_id in ai_agent.session_history:
        return {"session_id": session_id, "history": ai_agent.session_history[session_id]}
    raise HTTPException(status_code=404, detail="Session not found")

# ==================== SPECIALIZED CALCULATION ENDPOINTS ====================

@app.post("/api/calculate/material-comparison", response_model=MaterialPriceComparison, tags=["Calculations"])
async def calculate_material_comparison(request: SupplierComparisonRequest):
    """Compare material prices across suppliers"""
    try:
        return ai_agent.compare_material_prices(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calculate/profit-loss", response_model=ProfitLossCalculation, tags=["Calculations"])
async def calculate_profit_loss(production_data: dict):
    """Calculate profit & loss for production run"""
    try:
        return ai_agent.calculate_profit_loss(production_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calculate/gst", tags=["Calculations"])
async def calculate_gst(amount: float, is_interstate: bool = False):
    """Calculate GST for given amount (Tamil Nadu rates)"""
    try:
        return ai_agent.calculate_gst(amount, is_interstate)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calculate/employee-costs", response_model=List[EmployeeCostCalculation], tags=["Calculations"])
async def calculate_employee_costs(employee_data: Optional[dict] = None):
    """Calculate employee costs with Tamil Nadu welfare benefits"""
    try:
        return ai_agent.calculate_employee_costs(employee_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calculate/inventory", response_model=List[InventoryStatus], tags=["Calculations"])
async def get_inventory_status():
    """Get current inventory status for all materials"""
    try:
        return ai_agent.check_inventory_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calculate/machinery-recommendation", response_model=MachineryRecommendation, tags=["Calculations"])
async def get_machinery_recommendation(requirements: dict):
    """Get machinery recommendations based on production requirements"""
    try:
        return ai_agent.recommend_machinery(requirements)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calculate/workflow/{harness_type}", response_model=ProductionWorkflow, tags=["Calculations"])
async def get_production_workflow(harness_type: HarnessType):
    """Get automated production workflow for harness type"""
    try:
        return ai_agent.generate_production_workflow(harness_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SUPPLIER ENDPOINTS ====================

@app.get("/api/suppliers", tags=["Suppliers"])
async def get_all_suppliers(material_type: Optional[str] = None):
    """Get all suppliers or filter by material type"""
    if material_type:
        suppliers = ai_agent.get_supplier_recommendations(material_type)
        return [s.dict() for s in suppliers]
    
    return config.suppliers


@app.get("/api/suppliers/{supplier_id}", tags=["Suppliers"])
async def get_supplier(supplier_id: str):
    """Get specific supplier details"""
    for sup in config.suppliers:
        if sup["id"] == supplier_id:
            return sup
    raise HTTPException(status_code=404, detail="Supplier not found")

# ==================== COMPANY INFO ENDPOINTS ====================

@app.get("/api/company", tags=["Company"])
async def get_company_info():
    """Get company information"""
    return config.company


@app.get("/api/company/gst", tags=["Company"])
async def get_gst_info():
    """Get GST configuration for Tamil Nadu"""
    return {
        "state": config.gst["state"],
        "state_code": config.gst["state_code"],
        "cgst_rate": config.gst["cgst_rate"],
        "sgst_rate": config.gst["sgst_rate"],
        "igst_rate": config.gst["igst_rate"],
        "hsn_codes": config.gst["hsn_codes"],
        "gst_rates": config.gst_rates,
        "company_gstin": config.company["gstin"]
    }

# ==================== ERROR HANDLERS ====================

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)}
    )

# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    print("[STARTUP] Segan Industry API Starting...")
    print(f"   Company: {config['company']['name']}")
    print(f"   Location: {config['company']['address']}")
    print(f"   GSTIN: {config['company']['gstin']}")
    print("   AI Agent: Initialized")
    print("   Endpoints: Ready")


@app.on_event("shutdown")
async def shutdown_event():
    print("[SHUTDOWN] Segan Industry API Shutting down...")

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )