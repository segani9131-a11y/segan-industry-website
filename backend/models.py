from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class HarnessType(str, Enum):
    AUTOMOTIVE = "automotive"
    EV = "ev"
    INDUSTRIAL = "industrial"
    CONTROL_PANEL = "control_panel"
    CUSTOM = "custom"


class SupplierStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class QuotationStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ContactType(str, Enum):
    GENERAL = "general"
    QUOTATION = "quotation"
    SUPPORT = "support"
    PARTNERSHIP = "partnership"


# Request/Response Models
class MaterialRequest(BaseModel):
    material_type: str
    quantity: float
    unit: str


class SupplierComparisonRequest(BaseModel):
    material_type: str
    quantity: float
    unit: str
    location: str = "Chennai, Tamil Nadu"


class QuotationRequest(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    company_name: Optional[str] = None
    harness_type: HarnessType
    quantity: int
    wire_length_meters: float
    wire_gauge_mm2: float
    connector_count: int
    terminal_count: int
    special_requirements: Optional[str] = None
    delivery_location: str = "Chennai, Tamil Nadu"
    expected_delivery_days: int = 30


class QuotationItem(BaseModel):
    description: str
    quantity: float
    unit: str
    unit_price: float
    total_price: float
    gst_rate: float
    gst_amount: float
    hsn_code: str


class GSTBreakdown(BaseModel):
    cgst: float
    sgst: float
    igst: float
    total_gst: float
    is_interstate: bool


class QuotationResponse(BaseModel):
    quotation_id: str
    date: datetime
    validity_days: int
    customer_name: str
    customer_email: str
    harness_type: HarnessType
    items: List[QuotationItem]
    subtotal: float
    gst_breakdown: GSTBreakdown
    total_amount: float
    profit_margin_percent: float
    profit_amount: float
    overhead_amount: float
    contingency_amount: float
    payment_terms: str
    delivery_terms: str
    warranty_months: int
    status: QuotationStatus
    notes: Optional[str] = None


class ProductCatalogItem(BaseModel):
    id: str
    name: str
    description: str
    category: str
    specifications: Dict[str, Any]
    applications: List[str]
    certifications: List[str]
    min_order_quantity: int
    lead_time_days: int
    base_price_range: str


class AutomationService(BaseModel):
    id: str
    name: str
    description: str
    features: List[str]
    benefits: List[str]
    technologies: List[str]
    implementation_time: str
    price_range: str


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    company: Optional[str] = None
    contact_type: ContactType
    subject: str
    message: str


class ContactResponse(BaseModel):
    success: bool
    message: str
    reference_id: Optional[str] = None


class AgentRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


class AgentResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime
    actions: Optional[List[Dict[str, Any]]] = None


class SupplierInfo(BaseModel):
    id: str
    name: str
    location: str
    rating: float
    lead_time_days: int
    payment_terms: str
    materials: List[str]
    gst_compliant: bool
    status: SupplierStatus


class MaterialPriceComparison(BaseModel):
    material_type: str
    unit: str
    suppliers: List[Dict[str, Any]]
    best_price: float
    best_supplier: str
    savings_percent: float


class ProfitLossCalculation(BaseModel):
    revenue: float
    material_cost: float
    labor_cost: float
    overhead_cost: float
    machinery_cost: float
    total_cost: float
    gross_profit: float
    gross_margin_percent: float
    net_profit: float
    net_margin_percent: float
    gst_paid: float
    gst_collected: float
    gst_payable: float


class EmployeeCostCalculation(BaseModel):
    role: str
    count: int
    base_salary_monthly: float
    overtime_hours: float
    overtime_rate: float
    pf_contribution: float
    esi_contribution: float
    medical_insurance: float
    transport_allowance: float
    canteen_subsidy: float
    total_monthly_cost: float
    total_yearly_cost: float


class MachineryRecommendation(BaseModel):
    recommended_machines: List[Dict[str, Any]]
    total_investment: float
    yearly_maintenance: float
    power_consumption_kw: float
    estimated_roi_months: float
    production_capacity_per_month: int


class InventoryStatus(BaseModel):
    material: str
    current_stock: float
    unit: str
    reorder_point: float
    safety_stock: float
    status: str  # "OK", "LOW", "CRITICAL"
    days_remaining: int
    recommended_order_qty: float


class ProductionWorkflowStep(BaseModel):
    step_id: str
    name: str
    description: str
    machine_id: Optional[str] = None
    operator_role: str
    estimated_time_minutes: float
    quality_check: bool
    dependencies: List[str]


class ProductionWorkflow(BaseModel):
    harness_type: HarnessType
    steps: List[ProductionWorkflowStep]
    total_estimated_time_minutes: float
    required_machines: List[str]
    required_operators: Dict[str, int]
    quality_checkpoints: List[str]


# Database Models (for SQLAlchemy if needed)
class QuotationDB(BaseModel):
    id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    company_name: Optional[str]
    harness_type: str
    quantity: int
    specifications: Dict[str, Any]
    total_amount: float
    gst_breakdown: Dict[str, float]
    profit_margin: float
    status: str
    created_at: datetime
    updated_at: datetime
    valid_until: datetime


class ContactInquiryDB(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    company: Optional[str]
    contact_type: str
    subject: str
    message: str
    status: str
    created_at: datetime
    responded_at: Optional[datetime] = None


class SupplierDB(BaseModel):
    id: str
    name: str
    location: str
    rating: float
    lead_time_days: int
    payment_terms: str
    materials: List[str]
    gst_compliant: bool
    status: str
    created_at: datetime
    updated_at: datetime


class InventoryDB(BaseModel):
    id: str
    material_type: str
    current_stock: float
    unit: str
    reorder_point: float
    safety_stock: float
    last_updated: datetime
    last_order_date: Optional[datetime] = None