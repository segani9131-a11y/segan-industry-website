import json
import uuid
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from config import config
from models import (
    HarnessType, QuotationRequest, QuotationResponse, QuotationItem, GSTBreakdown,
    QuotationStatus, SupplierInfo, MaterialPriceComparison, ProfitLossCalculation,
    EmployeeCostCalculation, MachineryRecommendation, InventoryStatus,
    ProductionWorkflow, ProductionWorkflowStep, SupplierComparisonRequest,
    AgentRequest, AgentResponse
)


class WiringHarnessAIAgent:
    """AI Agent for Segan Industry Wiring Harness Manufacturing"""
    
    def __init__(self):
        self.config = config
        self.session_history = {}
        
        # Provide attribute-style access to config dict for backward compatibility
        self.materials = config.get("materials", {})
        self.suppliers = config.get("suppliers", [])
        self.machinery = config.get("machinery", [])
        self.quotation = config.get("quotation", {})
        self.gst = config.get("gst", {})
        self.gst_rates = config.get("gst_rates", {})
        self.employees = config.get("employees", {})
        self.production = config.get("production", {})
        self.inventory = config.get("inventory", {})
        self.company = config.get("company", {})
        self.ai_agent = config.get("ai_agent", {})
    
    def process_message(self, request: AgentRequest) -> AgentResponse:
        """Process natural language message and return AI response"""
        session_id = request.session_id or str(uuid.uuid4())[:8]
        
        if session_id not in self.session_history:
            self.session_history[session_id] = []
        
        self.session_history[session_id].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Analyze intent and route to appropriate handler
        response_text, actions = self._analyze_and_respond(request.message, request.context or {})
        
        self.session_history[session_id].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat()
        })
        
        return AgentResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.now(),
            actions=actions
        )
    
    def _analyze_and_respond(self, message: str, context: Dict) -> tuple:
        """Analyze message intent and generate response"""
        message_lower = message.lower()
        actions = []
        
        # Quotation generation
        if any(keyword in message_lower for keyword in ["quote", "quotation", "price", "cost", "estimate"]):
            if context.get("quotation_request"):
                quotation = self.generate_quotation(context["quotation_request"])
                actions.append({"type": "quotation_generated", "data": quotation.dict()})
                response = self._format_quotation_response(quotation)
            else:
                response = self._get_quotation_requirements()
        
        # Material price comparison
        elif any(keyword in message_lower for keyword in ["material", "price", "supplier", "compare", "copper", "wire", "connector"]):
            if context.get("material_request"):
                comparison = self.compare_material_prices(context["material_request"])
                actions.append({"type": "material_comparison", "data": comparison.dict()})
                response = self._format_material_comparison(comparison)
            else:
                response = self._get_material_requirements()
        
        # Profit & Loss calculation
        elif any(keyword in message_lower for keyword in ["profit", "loss", "margin", "pnl", "financial"]):
            if context.get("production_data"):
                pl = self.calculate_profit_loss(context["production_data"])
                actions.append({"type": "profit_loss", "data": pl.dict()})
                response = self._format_profit_loss(pl)
            else:
                response = self._get_profit_loss_requirements()
        
        # GST calculation
        elif any(keyword in message_lower for keyword in ["gst", "tax", "cgst", "sgst", "igst"]):
            if context.get("amount"):
                gst = self.calculate_gst(context["amount"], context.get("is_interstate", False))
                actions.append({"type": "gst_calculation", "data": gst})
                response = self._format_gst_response(gst, context["amount"])
            else:
                response = "Please provide the amount for GST calculation. For Tamil Nadu (intra-state): CGST 9% + SGST 9% = 18%. For inter-state: IGST 18%."
        
        # Employee welfare/cost calculation
        elif any(keyword in message_lower for keyword in ["employee", "staff", "salary", "welfare", "pf", "esi"]):
            if context.get("employee_data"):
                costs = self.calculate_employee_costs(context["employee_data"])
                actions.append({"type": "employee_costs", "data": [c.dict() for c in costs]})
                response = self._format_employee_costs(costs)
            else:
                response = self._get_employee_cost_summary()
        
        # Production workflow
        elif any(keyword in message_lower for keyword in ["workflow", "production", "process", "manufacturing", "assembly"]):
            if context.get("harness_type"):
                workflow = self.generate_production_workflow(context["harness_type"])
                actions.append({"type": "workflow", "data": workflow.dict()})
                response = self._format_workflow(workflow)
            else:
                response = "Please specify the harness type (automotive, ev, industrial, control_panel, custom) for production workflow."
        
        # Machinery recommendation
        elif any(keyword in message_lower for keyword in ["machine", "machinery", "equipment", "automation", "robot"]):
            if context.get("requirements"):
                machinery = self.recommend_machinery(context["requirements"])
                actions.append({"type": "machinery_recommendation", "data": machinery.dict()})
                response = self._format_machinery_recommendation(machinery)
            else:
                response = self._get_machinery_requirements()
        
        # Inventory tracking
        elif any(keyword in message_lower for keyword in ["inventory", "stock", "reorder", "shortage"]):
            inventory = self.check_inventory_status()
            actions.append({"type": "inventory_status", "data": [i.dict() for i in inventory]})
            response = self._format_inventory_status(inventory)
        
        # Supplier selection
        elif any(keyword in message_lower for keyword in ["supplier", "vendor", "source", "procurement"]):
            if context.get("material_type"):
                suppliers = self.get_supplier_recommendations(context["material_type"])
                actions.append({"type": "supplier_recommendations", "data": [s.dict() for s in suppliers]})
                response = self._format_supplier_recommendations(suppliers)
            else:
                response = self._get_all_suppliers_summary()
        
        # Automation services
        elif any(keyword in message_lower for keyword in ["automation", "ai agent", "workflow automation", "tracking"]):
            response = self._get_automation_services_info()
            actions.append({"type": "automation_info", "data": self._get_automation_services()})
        
        # Company info
        elif any(keyword in message_lower for keyword in ["company", "about", "segan", "profile", "contact", "chennai", "tamil nadu"]):
            response = self._get_company_info()
        
        # General help
        else:
            response = self._get_help_message()
        
        return response, actions
    
    # ==================== QUOTATION GENERATION ====================
    
    def generate_quotation(self, request: QuotationRequest) -> QuotationResponse:
        """Generate a complete wiring harness quotation with GST breakdown"""
        
        # Calculate material requirements
        wire_kg = self._calculate_wire_weight(request.wire_length_meters, request.wire_gauge_mm2)
        copper_cost = wire_kg * self.materials["copper_wire"]["base_price_per_kg"]
        
        pvc_wire_cost = request.wire_length_meters * self.materials["pvc_wire"]["base_price_per_meter"]
        connector_cost = request.connector_count * self.materials["connectors"]["base_price_per_unit"]
        terminal_cost = request.terminal_count * self.materials["terminals"]["base_price_per_unit"]
        
        # Additional materials (tape, heat shrink, corrugated tube)
        tape_rolls = max(1, math.ceil(request.wire_length_meters / 50))
        tape_cost = tape_rolls * self.materials["tape_pvc"]["base_price_per_roll"]
        
        heat_shrink_m = request.wire_length_meters * 0.1  # 10% of wire length
        heat_shrink_cost = heat_shrink_m * self.materials["heat_shrink"]["base_price_per_meter"]
        
        corrugated_m = request.wire_length_meters * 0.8  # 80% coverage
        corrugated_cost = corrugated_m * self.materials["corrugated_tube"]["base_price_per_meter"]
        
        material_cost = copper_cost + pvc_wire_cost + connector_cost + terminal_cost + tape_cost + heat_shrink_cost + corrugated_cost
        
        # Labor cost calculation
        labor_hours = self._calculate_labor_hours(request.harness_type, request.quantity, request.wire_length_meters)
        labor_rate_per_hour = 250  # INR per hour average
        labor_cost = labor_hours * labor_rate_per_hour
        
        # Overhead (15% of material + labor)
        overhead_percent = self.quotation["overhead_percentage"]
        overhead = (material_cost + labor_cost) * (overhead_percent / 100)
        
        # Contingency (5%)
        contingency_percent = self.quotation["contingency_percentage"]
        contingency = (material_cost + labor_cost + overhead) * (contingency_percent / 100)
        
        # Subtotal before profit
        subtotal = material_cost + labor_cost + overhead + contingency
        
        # Profit margin
        profit_margin = self.quotation["profit_margin_percent"]
        profit = subtotal * (profit_margin / 100)
        
        # Total before GST
        total_before_gst = subtotal + profit
        
        # GST Calculation (Tamil Nadu - Intra-state: CGST 9% + SGST 9%)
        is_interstate = "tamil nadu" not in request.delivery_location.lower() and "chennai" not in request.delivery_location.lower()
        gst_rate = self.gst_rates["wiring_harness"]
        
        if is_interstate:
            igst = total_before_gst * (gst_rate / 100)
            cgst = 0
            sgst = 0
        else:
            cgst = total_before_gst * (self.gst["cgst_rate"] / 100)
            sgst = total_before_gst * (self.gst["sgst_rate"] / 100)
            igst = 0
        
        total_gst = cgst + sgst + igst
        total_amount = total_before_gst + total_gst
        
        # Build quotation items
        items = [
            QuotationItem(
                description=f"Copper Wire ({request.wire_gauge_mm2} mm²)",
                quantity=wire_kg,
                unit="kg",
                unit_price=self.materials["copper_wire"]["base_price_per_kg"],
                total_price=copper_cost,
                gst_rate=gst_rate,
                gst_amount=copper_cost * (gst_rate / 100),
                hsn_code=self.gst["hsn_codes"]["wiring_harness"]
            ),
            QuotationItem(
                description="PVC Insulated Wire",
                quantity=request.wire_length_meters,
                unit="meter",
                unit_price=self.materials["pvc_wire"]["base_price_per_meter"],
                total_price=pvc_wire_cost,
                gst_rate=gst_rate,
                gst_amount=pvc_wire_cost * (gst_rate / 100),
                hsn_code=self.gst["hsn_codes"]["wiring_harness"]
            ),
            QuotationItem(
                description="Connectors",
                quantity=request.connector_count,
                unit="piece",
                unit_price=self.materials["connectors"]["base_price_per_unit"],
                total_price=connector_cost,
                gst_rate=gst_rate,
                gst_amount=connector_cost * (gst_rate / 100),
                hsn_code=self.gst["hsn_codes"]["connectors"]
            ),
            QuotationItem(
                description="Terminals",
                quantity=request.terminal_count,
                unit="piece",
                unit_price=self.materials["terminals"]["base_price_per_unit"],
                total_price=terminal_cost,
                gst_rate=gst_rate,
                gst_amount=terminal_cost * (gst_rate / 100),
                hsn_code=self.gst["hsn_codes"]["terminals"]
            ),
            QuotationItem(
                description="PVC Tape",
                quantity=tape_rolls,
                unit="roll",
                unit_price=self.materials["tape_pvc"]["base_price_per_roll"],
                total_price=tape_cost,
                gst_rate=gst_rate,
                gst_amount=tape_cost * (gst_rate / 100),
                hsn_code=self.gst["hsn_codes"]["wiring_harness"]
            ),
            QuotationItem(
                description="Heat Shrink Tubing",
                quantity=heat_shrink_m,
                unit="meter",
                unit_price=self.materials["heat_shrink"]["base_price_per_meter"],
                total_price=heat_shrink_cost,
                gst_rate=gst_rate,
                gst_amount=heat_shrink_cost * (gst_rate / 100),
                hsn_code=self.gst["hsn_codes"]["wiring_harness"]
            ),
            QuotationItem(
                description="Corrugated Tube",
                quantity=corrugated_m,
                unit="meter",
                unit_price=self.materials["corrugated_tube"]["base_price_per_meter"],
                total_price=corrugated_cost,
                gst_rate=gst_rate,
                gst_amount=corrugated_cost * (gst_rate / 100),
                hsn_code=self.gst["hsn_codes"]["wiring_harness"]
            ),
            QuotationItem(
                description="Labor & Assembly",
                quantity=labor_hours,
                unit="hours",
                unit_price=labor_rate_per_hour,
                total_price=labor_cost,
                gst_rate=gst_rate,
                gst_amount=labor_cost * (gst_rate / 100),
                hsn_code=self.gst["hsn_codes"]["wiring_harness"]
            ),
            QuotationItem(
                description="Overhead & Factory Costs",
                quantity=1,
                unit="lot",
                unit_price=overhead,
                total_price=overhead,
                gst_rate=gst_rate,
                gst_amount=overhead * (gst_rate / 100),
                hsn_code=self.gst["hsn_codes"]["wiring_harness"]
            ),
            QuotationItem(
                description="Contingency (5%)",
                quantity=1,
                unit="lot",
                unit_price=contingency,
                total_price=contingency,
                gst_rate=gst_rate,
                gst_amount=contingency * (gst_rate / 100),
                hsn_code=self.gst["hsn_codes"]["wiring_harness"]
            )
        ]
        
        quotation_id = f"SI-QT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        
        return QuotationResponse(
            quotation_id=quotation_id,
            date=datetime.now(),
            validity_days=self.quotation["validity_days"],
            customer_name=request.customer_name,
            customer_email=request.customer_email,
            harness_type=request.harness_type,
            items=items,
            subtotal=total_before_gst,
            gst_breakdown=GSTBreakdown(
                cgst=round(cgst, 2),
                sgst=round(sgst, 2),
                igst=round(igst, 2),
                total_gst=round(total_gst, 2),
                is_interstate=is_interstate
            ),
            total_amount=round(total_amount, 2),
            profit_margin_percent=profit_margin,
            profit_amount=round(profit, 2),
            overhead_amount=round(overhead, 2),
            contingency_amount=round(contingency, 2),
            payment_terms=self.quotation["payment_terms"],
            delivery_terms=self.quotation["delivery_terms"],
            warranty_months=self.quotation["warranty_months"],
            status=QuotationStatus.DRAFT,
            notes=request.special_requirements
        )
    
    def _calculate_wire_weight(self, length_meters: float, gauge_mm2: float) -> float:
        """Calculate copper wire weight in kg"""
        # Copper density: 8.96 g/cm³
        # Cross-sectional area in mm², length in meters
        # Weight (kg) = length(m) * area(mm²) * density(g/cm³) / 1000
        # 1 mm² = 0.01 cm², so weight = length * area * 8.96 * 0.01 / 1000 = length * area * 0.0000896
        return round(length_meters * gauge_mm2 * 0.00896, 3)
    
    def _calculate_labor_hours(self, harness_type: HarnessType, quantity: int, wire_length: float) -> float:
        """Calculate labor hours based on harness type and complexity"""
        base_hours_per_unit = {
            HarnessType.AUTOMOTIVE: 2.5,
            HarnessType.EV: 3.5,
            HarnessType.INDUSTRIAL: 2.0,
            HarnessType.CONTROL_PANEL: 1.5,
            HarnessType.CUSTOM: 4.0
        }
        base = base_hours_per_unit.get(harness_type, 2.5)
        # Add complexity factor for wire length
        length_factor = 1 + (wire_length / 100) * 0.1
        return round(base * quantity * length_factor, 1)
    
    def _format_quotation_response(self, quotation: QuotationResponse) -> str:
        """Format quotation as readable response"""
        gst = quotation.gst_breakdown
        gst_type = "IGST (Inter-state)" if gst.is_interstate else "CGST + SGST (Intra-state Tamil Nadu)"
        
        response = f"""
🏢 **SEGAN INDUSTRY PRIVATE LIMITED**
**Quotation: {quotation.quotation_id}**
Date: {quotation.date.strftime('%d-%m-%Y')} | Valid for: {quotation.validity_days} days

👤 **Customer:** {quotation.customer_name} ({quotation.customer_email})
🔧 **Harness Type:** {quotation.harness_type.value.title()}
📦 **Quantity:** {sum(int(item.quantity) for item in quotation.items if item.unit in ['piece', 'kg'])} sets

---

**📋 QUOTATION DETAILS:**

"""
        for item in quotation.items:
            response += f"• {item.description}: {item.quantity} {item.unit} × ₹{item.unit_price:,.2f} = **₹{item.total_price:,.2f}** (GST {item.gst_rate}%)\n"
        
        response += f"""
---
**Subtotal (before GST):** ₹{quotation.subtotal:,.2f}
**Profit Margin ({quotation.profit_margin_percent}%):** ₹{quotation.profit_amount:,.2f}
**Overhead:** ₹{quotation.overhead_amount:,.2f}
**Contingency:** ₹{quotation.contingency_amount:,.2f}

**🧾 GST BREAKDOWN ({gst_type}):**
• CGST ({self.gst['cgst_rate']}%): ₹{gst.cgst:,.2f}
• SGST ({self.gst['sgst_rate']}%): ₹{gst.sgst:,.2f}
• IGST ({self.gst['igst_rate']}%): ₹{gst.igst:,.2f}
• **Total GST:** ₹{gst.total_gst:,.2f}

---

💰 **GRAND TOTAL: ₹{quotation.total_amount:,.2f}**

📋 **Terms & Conditions:**
• Payment: {quotation.payment_terms}
• Delivery: {quotation.delivery_terms}
• Warranty: {quotation.warranty_months} months
• Validity: {quotation.validity_days} days from quote date
• GSTIN: {self.company['gstin']}
• HSN Code: {self.gst['hsn_codes']['wiring_harness']}

*Quotation generated by Segan Industry AI Agent*
"""
        return response
    
    def _get_quotation_requirements(self) -> str:
        return """
📋 **Quotation Requirements for Wiring Harness:**

Please provide the following details for an accurate quotation:

1. **Customer Details:** Name, Email, Phone, Company
2. **Harness Type:** Automotive / EV / Industrial / Control Panel / Custom
3. **Quantity:** Number of harness sets required
4. **Wire Specifications:**
   - Total wire length per harness (meters)
   - Wire gauge (mm²) - e.g., 0.5, 0.75, 1.0, 1.5, 2.5, 4.0, 6.0
5. **Components:**
   - Number of connectors
   - Number of terminals
6. **Delivery Location:** City, State (for GST calculation)
7. **Special Requirements:** Any specific standards, certifications, testing needs
8. **Expected Delivery Timeline:** Days required

**GST Note:** For Tamil Nadu (Chennai) deliveries: CGST 9% + SGST 9% = 18%
For Inter-state: IGST 18%

Reply with these details and I'll generate a complete quotation with GST breakdown, profit margins, and terms.
"""
    
    # ==================== MATERIAL PRICE COMPARISON ====================
    
    def compare_material_prices(self, request: SupplierComparisonRequest) -> MaterialPriceComparison:
        """Compare material prices across suppliers"""
        material = self.materials.get(request.material_type.lower().replace(" ", "_"))
        if not material:
            raise ValueError(f"Material '{request.material_type}' not found")
        
        supplier_details = []
        for sup_id in material["suppliers"]:
            supplier = next((s for s in self.suppliers if s["id"] == sup_id), None)
            if supplier and supplier["status"] == "active":
                # Add some price variation per supplier (±5%)
                import random
                variation = 1 + (random.uniform(-0.05, 0.05))
                unit_price = material[f"base_price_per_{request.unit}"] * variation if f"base_price_per_{request.unit}" in material else material["base_price_per_kg"] * variation
                
                total_price = unit_price * request.quantity
                gst_amount = total_price * (material["gst_rate"] / 100)
                
                supplier_details.append({
                    "supplier_id": supplier["id"],
                    "supplier_name": supplier["name"],
                    "location": supplier["location"],
                    "rating": supplier["rating"],
                    "lead_time_days": supplier["lead_time_days"],
                    "payment_terms": supplier["payment_terms"],
                    "unit_price": round(unit_price, 2),
                    "total_price": round(total_price, 2),
                    "gst_amount": round(gst_amount, 2),
                    "total_with_gst": round(total_price + gst_amount, 2),
                    "gst_compliant": supplier["gst_compliant"]
                })
        
        # Sort by total price
        supplier_details.sort(key=lambda x: x["total_with_gst"])
        
        best = supplier_details[0] if supplier_details else {}
        worst = supplier_details[-1] if supplier_details else {}
        savings = 0
        if best and worst:
            savings = ((worst["total_with_gst"] - best["total_with_gst"]) / worst["total_with_gst"]) * 100
        
        return MaterialPriceComparison(
            material_type=request.material_type,
            unit=request.unit,
            suppliers=supplier_details,
            best_price=best.get("total_with_gst", 0),
            best_supplier=best.get("supplier_name", ""),
            savings_percent=round(savings, 1)
        )
    
    def _format_material_comparison(self, comparison: MaterialPriceComparison) -> str:
        response = f"""
📊 **Material Price Comparison: {comparison.material_type} ({comparison.unit})**

**Best Price:** ₹{comparison.best_price:,.2f} from **{comparison.best_supplier}**
**Potential Savings:** {comparison.savings_percent}%

**Supplier Details:**
"""
        for i, sup in enumerate(comparison.suppliers, 1):
            response += f"""
{i}. **{sup['supplier_name']}** ({sup['location']})
   ⭐ Rating: {sup['rating']}/5 | ⏱️ Lead Time: {sup['lead_time_days']} days | 💳 Terms: {sup['payment_terms']}
   💰 Unit Price: ₹{sup['unit_price']:,.2f}/{comparison.unit} | Total: ₹{sup['total_price']:,.2f} + GST ₹{sup['gst_amount']:,.2f} = **₹{sup['total_with_gst']:,.2f}**
   ✅ GST Compliant: {'Yes' if sup['gst_compliant'] else 'No'}
"""
        return response
    
    def _get_material_requirements(self) -> str:
        materials = list(self.config.materials.keys())
        return f"""
📦 **Available Materials for Price Comparison:**
{', '.join(materials)}

Please specify:
1. Material type
2. Quantity needed
3. Unit (kg, meter, piece, roll)
4. Delivery location (for GST calculation)

Example: "Compare copper wire prices for 500 kg delivery to Chennai"
"""
    
    # ==================== PROFIT & LOSS CALCULATION ====================
    
    def calculate_profit_loss(self, production_data: Dict) -> ProfitLossCalculation:
        """Calculate comprehensive profit & loss for production"""
        
        quantity = production_data.get("quantity", 100)
        harness_type = production_data.get("harness_type", "automotive")
        wire_length = production_data.get("wire_length_meters", 50)
        wire_gauge = production_data.get("wire_gauge_mm2", 1.0)
        connector_count = production_data.get("connector_count", 20)
        terminal_count = production_data.get("terminal_count", 40)
        selling_price_per_unit = production_data.get("selling_price_per_unit", 0)
        
        # Calculate material cost per unit
        wire_kg = self._calculate_wire_weight(wire_length, wire_gauge)
        copper_cost = wire_kg * self.materials["copper_wire"]["base_price_per_kg"]
        pvc_cost = wire_length * self.materials["pvc_wire"]["base_price_per_meter"]
        connector_cost = connector_count * self.materials["connectors"]["base_price_per_unit"]
        terminal_cost = terminal_count * self.materials["terminals"]["base_price_per_unit"]
        
        tape_rolls = max(1, math.ceil(wire_length / 50))
        tape_cost = tape_rolls * self.materials["tape_pvc"]["base_price_per_roll"]
        
        heat_shrink_m = wire_length * 0.1
        heat_shrink_cost = heat_shrink_m * self.materials["heat_shrink"]["base_price_per_meter"]
        
        corrugated_m = wire_length * 0.8
        corrugated_cost = corrugated_m * self.materials["corrugated_tube"]["base_price_per_meter"]
        
        material_cost_per_unit = copper_cost + pvc_cost + connector_cost + terminal_cost + tape_cost + heat_shrink_cost + corrugated_cost
        total_material_cost = material_cost_per_unit * quantity
        
        # Labor cost
        labor_hours_per_unit = self._calculate_labor_hours(HarnessType(harness_type), 1, wire_length)
        labor_rate = 250
        labor_cost_per_unit = labor_hours_per_unit * labor_rate
        total_labor_cost = labor_cost_per_unit * quantity
        
        # Overhead (15%)
        overhead_percent = self.quotation["overhead_percentage"]
        total_overhead = (total_material_cost + total_labor_cost) * (overhead_percent / 100)
        
        # Machinery cost (depreciation + maintenance)
        machinery_cost = self._calculate_machinery_cost(quantity)
        
        total_cost = total_material_cost + total_labor_cost + total_overhead + machinery_cost
        
        # Revenue
        if selling_price_per_unit == 0:
            # Calculate based on quotation logic
            profit_margin = self.quotation["profit_margin_percent"]
            contingency = total_cost * (self.quotation["contingency_percentage"] / 100)
            cost_with_contingency = total_cost + contingency
            selling_price_per_unit = (cost_with_contingency * (1 + profit_margin / 100)) / quantity
        
        revenue = selling_price_per_unit * quantity
        
        # GST Calculations
        gst_rate = self.gst_rates["wiring_harness"]
        gst_collected = revenue * (gst_rate / 100)
        gst_paid = (total_material_cost + total_labor_cost + total_overhead) * (gst_rate / 100)
        gst_payable = gst_collected - gst_paid
        
        gross_profit = revenue - total_material_cost - total_labor_cost
        gross_margin = (gross_profit / revenue) * 100 if revenue > 0 else 0
        
        net_profit = revenue - total_cost
        net_margin = (net_profit / revenue) * 100 if revenue > 0 else 0
        
        return ProfitLossCalculation(
            revenue=round(revenue, 2),
            material_cost=round(total_material_cost, 2),
            labor_cost=round(total_labor_cost, 2),
            overhead_cost=round(total_overhead, 2),
            machinery_cost=round(machinery_cost, 2),
            total_cost=round(total_cost, 2),
            gross_profit=round(gross_profit, 2),
            gross_margin_percent=round(gross_margin, 1),
            net_profit=round(net_profit, 2),
            net_margin_percent=round(net_margin, 1),
            gst_paid=round(gst_paid, 2),
            gst_collected=round(gst_collected, 2),
            gst_payable=round(gst_payable, 2)
        )
    
    def _calculate_machinery_cost(self, quantity: int) -> float:
        """Calculate machinery depreciation and maintenance cost per production run"""
        total_machine_cost = 0
        for machine in self.machinery:
            # Depreciation over 10 years, maintenance yearly
            depreciation_per_unit = machine["price_inr"] / (10 * 12 * 26 * 8 / 0.5)  # per hour
            maintenance_per_unit = machine["maintenance_cost_yearly"] / (12 * 26 * 8 / 0.5)  # per hour
            
            # Estimate hours needed for this quantity
            hours_needed = quantity * 0.5  # rough estimate
            total_machine_cost += (depreciation_per_unit + maintenance_per_unit) * hours_needed
        
        return total_machine_cost
    
    def _format_profit_loss(self, pl: ProfitLossCalculation) -> str:
        return f"""
📊 **PROFIT & LOSS STATEMENT - Segan Industry**

**💰 REVENUE:** ₹{pl.revenue:,.2f}

**📉 COSTS:**
• Raw Materials: ₹{pl.material_cost:,.2f}
• Direct Labor: ₹{pl.labor_cost:,.2f}
• Factory Overhead: ₹{pl.overhead_cost:,.2f}
• Machinery (Depreciation + Maintenance): ₹{pl.machinery_cost:,.2f}
• **Total Cost: ₹{pl.total_cost:,.2f}**

**📈 PROFITABILITY:**
• Gross Profit: ₹{pl.gross_profit:,.2f} ({pl.gross_margin_percent}%)
• Net Profit: ₹{pl.net_profit:,.2f} ({pl.net_margin_percent}%)

**🧾 GST SUMMARY (18%):**
• GST Paid on Inputs: ₹{pl.gst_paid:,.2f}
• GST Collected on Sales: ₹{pl.gst_collected:,.2f}
• **GST Payable (Net): ₹{pl.gst_payable:,.2f}**

**📊 KEY METRICS:**
• Break-even Point: {pl.total_cost / (pl.revenue / max(1, 100)):.0f} units
• Profit per Unit: ₹{pl.net_profit / max(1, 100):,.2f}
• ROI: {(pl.net_profit / pl.total_cost * 100) if pl.total_cost > 0 else 0:.1f}%
"""
    
    def _get_profit_loss_requirements(self) -> str:
        return """
📊 **Profit & Loss Calculation Requirements:**

Please provide:
1. **Production Quantity:** Number of harness sets
2. **Harness Type:** automotive / ev / industrial / control_panel / custom
3. **Wire Specs:** Length (meters) and Gauge (mm²) per harness
4. **Components:** Connector count and Terminal count per harness
5. **Selling Price:** Target selling price per unit (optional - will calculate based on 18% margin)

Example: "Calculate P&L for 500 automotive harnesses, 50m length, 1mm² wire, 20 connectors, 40 terminals"
"""
    
    # ==================== GST CALCULATION ====================
    
    def calculate_gst(self, amount: float, is_interstate: bool = False) -> Dict:
        """Calculate GST for Tamil Nadu (Intra-state: CGST+SGST, Inter-state: IGST)"""
        gst_rate = self.gst_rates["wiring_harness"]  # 18%
        
        if is_interstate:
            igst = amount * (gst_rate / 100)
            return {
                "cgst": 0,
                "sgst": 0,
                "igst": round(igst, 2),
                "total_gst": round(igst, 2),
                "total_with_gst": round(amount + igst, 2),
                "type": "IGST (Inter-state)"
            }
        else:
            cgst = amount * (self.gst["cgst_rate"] / 100)
            sgst = amount * (self.gst["sgst_rate"] / 100)
            total_gst = cgst + sgst
            return {
                "cgst": round(cgst, 2),
                "sgst": round(sgst, 2),
                "igst": 0,
                "total_gst": round(total_gst, 2),
                "total_with_gst": round(amount + total_gst, 2),
                "type": "CGST + SGST (Intra-state Tamil Nadu)"
            }
    
    def _format_gst_response(self, gst: Dict, amount: float) -> str:
        return f"""
🧾 **GST CALCULATION - Segan Industry (Tamil Nadu, GSTIN: {self.company['gstin']})**

**Base Amount:** ₹{amount:,.2f}
**GST Type:** {gst['type']}
**GST Rate:** {self.gst_rates['wiring_harness']}%

**Breakdown:**
• CGST ({self.gst['cgst_rate']}%): ₹{gst['cgst']:,.2f}
• SGST ({self.gst['sgst_rate']}%): ₹{gst['sgst']:,.2f}
• IGST ({self.gst['igst_rate']}%): ₹{gst['igst']:,.2f}
• **Total GST: ₹{gst['total_gst']:,.2f}**

**Total with GST: ₹{gst['total_with_gst']:,.2f}**

**HSN Code:** {self.gst['hsn_codes']['wiring_harness']} (Wiring Harness)
**Place of Supply:** {self.company['address']}
"""
    
    # ==================== EMPLOYEE WELFARE & COST CALCULATION ====================
    
    def calculate_employee_costs(self, employee_data: Dict = None) -> List[EmployeeCostCalculation]:
        """Calculate employee costs with welfare benefits (Tamil Nadu labor laws)"""
        if employee_data is None:
            employee_data = {"categories": self.config.employees["categories"]}
        
        results = []
        welfare = self.config.employees["welfare"]
        
        for cat in employee_data.get("categories", self.config.employees["categories"]):
            count = cat["count"]
            base_salary = cat["salary_monthly"]
            overtime_hours = cat.get("overtime_hours", self.config.production["overtime_hours_per_month"])
            overtime_rate = cat.get("overtime_rate", 1.5)
            
            # Monthly calculations
            overtime_pay = base_salary / 26 / 8 * overtime_hours * overtime_rate
            gross_monthly = base_salary + overtime_pay
            
            # Statutory contributions (Employer share)
            pf_contribution = min(gross_monthly, 15000) * (welfare["pf_rate"] / 100)  # PF on max 15000
            esi_contribution = gross_monthly * (welfare["esi_rate"] / 100) if gross_monthly <= 21000 else 0
            
            # Welfare benefits
            medical_insurance = welfare["medical_insurance_per_employee_yearly"] / 12
            transport = welfare["transport_allowance_monthly"]
            canteen = welfare["canteen_subsidy_per_meal"] * 2 * 26  # 2 meals/day, 26 days
            
            total_monthly = gross_monthly + pf_contribution + esi_contribution + medical_insurance + transport + canteen
            total_yearly = total_monthly * 12 + base_salary * (welfare["bonus_percentage"] / 100)  # Annual bonus
            
            results.append(EmployeeCostCalculation(
                role=cat["role"],
                count=count,
                base_salary_monthly=base_salary,
                overtime_hours=overtime_hours,
                overtime_rate=overtime_rate,
                pf_contribution=round(pf_contribution, 2),
                esi_contribution=round(esi_contribution, 2),
                medical_insurance=round(medical_insurance, 2),
                transport_allowance=round(transport, 2),
                canteen_subsidy=round(canteen, 2),
                total_monthly_cost=round(total_monthly, 2),
                total_yearly_cost=round(total_yearly, 2)
            ))
        
        return results
    
    def _format_employee_costs(self, costs: List[EmployeeCostCalculation]) -> str:
        total_monthly = sum(c.total_monthly_cost * c.count for c in costs)
        total_yearly = sum(c.total_yearly_cost * c.count for c in costs)
        
        response = f"""
👥 **EMPLOYEE COST ANALYSIS - Segan Industry (Tamil Nadu Labor Laws)**

**Statutory Rates (TN):**
• PF (Employer): {self.config.employees['welfare']['pf_rate']}% (on ₹15,000 max)
• ESI (Employer): {self.config.employees['welfare']['esi_rate']}% (on ₹21,000 max)
• Bonus: {self.config.employees['welfare']['bonus_percentage']}% (annual)
• Annual Leave: {self.config.employees['welfare']['leave_days_annual']} days

---

"""
        for cost in costs:
            response += f"""
**{cost.role}** ({cost.count} employees)
• Base Salary: ₹{cost.base_salary_monthly:,.2f}/month
• Overtime: {cost.overtime_hours} hrs @ {cost.overtime_rate}x = ₹{(cost.base_salary_monthly/26/8*cost.overtime_hours*cost.overtime_rate):,.2f}
• PF (Employer): ₹{cost.pf_contribution:,.2f}
• ESI (Employer): ₹{cost.esi_contribution:,.2f}
• Medical Insurance: ₹{cost.medical_insurance:,.2f}
• Transport Allowance: ₹{cost.transport_allowance:,.2f}
• Canteen Subsidy: ₹{cost.canteen_subsidy:,.2f}
• **Total Monthly/Employee: ₹{cost.total_monthly_cost:,.2f}**
• **Total Yearly/Employee: ₹{cost.total_yearly_cost:,.2f}**
• **Total for {cost.count} employees: ₹{cost.total_monthly_cost * cost.count:,.2f}/month | ₹{cost.total_yearly_cost * cost.count:,.2f}/year**
"""
        
        response += f"""
---

📊 **TOTAL WORKFORCE COST:**
• **Monthly: ₹{total_monthly:,.2f}**
• **Yearly: ₹{total_yearly:,.2f}**
• **Total Employees: {sum(c.count for c in costs)}**

*Compliant with Tamil Nadu Factories Act, 1948 & TN Labour Welfare Fund*
"""
        return response
    
    def _get_employee_cost_summary(self) -> str:
        costs = self.calculate_employee_costs()
        return self._format_employee_costs(costs)
    
    # ==================== PRODUCTION WORKFLOW AUTOMATION ====================
    
    def generate_production_workflow(self, harness_type: HarnessType) -> ProductionWorkflow:
        """Generate automated production workflow for harness type"""
        
        workflows = {
            HarnessType.AUTOMOTIVE: [
                ProductionWorkflowStep("STEP01", "Wire Cutting & Stripping", "Cut wires to length and strip insulation", "MCH001", "Wire Cutting Operator", 15, True, []),
                ProductionWorkflowStep("STEP02", "Terminal Crimping", "Crimp terminals on wire ends", "MCH002", "Crimping Operator", 20, True, ["STEP01"]),
                ProductionWorkflowStep("STEP03", "Connector Assembly", "Insert terminals into connector housings", None, "Assembly Operator", 15, True, ["STEP02"]),
                ProductionWorkflowStep("STEP04", "Wire Routing & Taping", "Route wires per layout and apply PVC tape", "MCH004", "Assembly Operator", 25, True, ["STEP03"]),
                ProductionWorkflowStep("STEP05", "Heat Shrink Application", "Apply heat shrink tubing at transitions", None, "Assembly Operator", 10, True, ["STEP04"]),
                ProductionWorkflowStep("STEP06", "Corrugated Tube Installation", "Install protective corrugated tubing", None, "Assembly Operator", 15, False, ["STEP05"]),
                ProductionWorkflowStep("STEP07", "Continuity Testing", "Test all circuits for continuity", "MCH005", "Quality Inspector", 10, True, ["STEP06"]),
                ProductionWorkflowStep("STEP08", "Hipot/Insulation Test", "High voltage insulation testing", "MCH005", "Quality Inspector", 15, True, ["STEP07"]),
                ProductionWorkflowStep("STEP09", "Visual Inspection", "Final visual quality check", None, "Quality Inspector", 10, True, ["STEP08"]),
                ProductionWorkflowStep("STEP10", "Packaging & Labeling", "Pack in ESD bags with labels", None, "Store Keeper", 10, False, ["STEP09"]),
            ],
            HarnessType.EV: [
                ProductionWorkflowStep("STEP01", "HV Wire Cutting & Stripping", "Cut high-voltage cables with special tools", "MCH001", "Wire Cutting Operator", 20, True, []),
                ProductionWorkflowStep("STEP02", "HV Terminal Crimping", "Crimp high-voltage terminals (orange)", "MCH002", "Crimping Operator", 25, True, ["STEP01"]),
                ProductionWorkflowStep("STEP03", "HV Connector Assembly", "Assemble HV connectors with shielding", None, "Assembly Operator", 30, True, ["STEP02"]),
                ProductionWorkflowStep("STEP04", "Shielding & Grounding", "Apply EMI shielding and grounding", None, "Assembly Operator", 20, True, ["STEP03"]),
                ProductionWorkflowStep("STEP05", "LV Wire Processing", "Process low-voltage signal wires", "MCH001", "Wire Cutting Operator", 15, True, ["STEP01"]),
                ProductionWorkflowStep("STEP06", "Full Harness Assembly", "Integrate HV and LV sections", None, "Assembly Operator", 40, True, ["STEP04", "STEP05"]),
                ProductionWorkflowStep("STEP07", "HV Continuity Test", "High-voltage continuity verification", "MCH005", "Quality Inspector", 20, True, ["STEP06"]),
                ProductionWorkflowStep("STEP08", "Insulation Resistance Test", "Megger test at 1000V DC", "MCH005", "Quality Inspector", 15, True, ["STEP07"]),
                ProductionWorkflowStep("STEP09", "Partial Discharge Test", "PD testing for HV harnesses", "MCH005", "Quality Inspector", 20, True, ["STEP08"]),
                ProductionWorkflowStep("STEP10", "Final Inspection & Pack", "Visual, dimensional, packaging", None, "Quality Inspector", 15, True, ["STEP09"]),
            ],
            HarnessType.INDUSTRIAL: [
                ProductionWorkflowStep("STEP01", "Wire Preparation", "Cut and strip industrial gauge wires", "MCH003", "Wire Cutting Operator", 10, True, []),
                ProductionWorkflowStep("STEP02", "Terminal Crimping", "Crimp ring/fork terminals", "MCH002", "Crimping Operator", 15, True, ["STEP01"]),
                ProductionWorkflowStep("STEP03", "Terminal Block Assembly", "Mount terminals on DIN rails/blocks", None, "Assembly Operator", 20, True, ["STEP02"]),
                ProductionWorkflowStep("STEP04", "Wire Ducting", "Route wires in cable ducts", None, "Assembly Operator", 15, False, ["STEP03"]),
                ProductionWorkflowStep("STEP05", "Ferrule Crimping", "Crimp wire ferrules for PLC connections", "MCH002", "Crimping Operator", 10, True, ["STEP01"]),
                ProductionWorkflowStep("STEP06", "Continuity Check", "Point-to-point continuity", "MCH005", "Quality Inspector", 10, True, ["STEP04", "STEP05"]),
                ProductionWorkflowStep("STEP07", "Labeling & Documentation", "Wire marking and as-built drawings", None, "Quality Inspector", 10, False, ["STEP06"]),
            ],
            HarnessType.CONTROL_PANEL: [
                ProductionWorkflowStep("STEP01", "Wire Cutting & Ferrule Crimping", "Cut wires and crimp ferrules", "MCH003", "Wire Cutting Operator", 15, True, []),
                ProductionWorkflowStep("STEP02", "PLC I/O Wiring", "Wire PLC input/output modules", None, "Assembly Operator", 30, True, ["STEP01"]),
                ProductionWorkflowStep("STEP03", "Power Circuit Wiring", "Wire contactors, breakers, drives", None, "Assembly Operator", 25, True, ["STEP01"]),
                ProductionWorkflowStep("STEP04", "Terminal Block Wiring", "Complete terminal block connections", None, "Assembly Operator", 20, True, ["STEP02", "STEP03"]),
                ProductionWorkflowStep("STEP05", "Wire Ducting & Tie-offs", "Organize in wire ducts", None, "Assembly Operator", 15, False, ["STEP04"]),
                ProductionWorkflowStep("STEP06", "Power-up Test", "Functional test with 24V/230V", "MCH005", "Quality Inspector", 20, True, ["STEP05"]),
                ProductionWorkflowStep("STEP07", "Final Inspection", "Visual, torque check, labeling", None, "Quality Inspector", 10, True, ["STEP06"]),
            ]
        }
        
        steps = workflows.get(harness_type, workflows[HarnessType.CUSTOM])
        total_time = sum(s.estimated_time_minutes for s in steps)
        required_machines = list(set(s.machine_id for s in steps if s.machine_id))
        
        operator_counts = {}
        for step in steps:
            role = step.operator_role
            operator_counts[role] = operator_counts.get(role, 0) + 1
        
        quality_checkpoints = [s.name for s in steps if s.quality_check]
        
        return ProductionWorkflow(
            harness_type=harness_type,
            steps=steps,
            total_estimated_time_minutes=total_time,
            required_machines=required_machines,
            required_operators=operator_counts,
            quality_checkpoints=quality_checkpoints
        )
    
    def _format_workflow(self, workflow: ProductionWorkflow) -> str:
        response = f"""
🏭 **PRODUCTION WORKFLOW AUTOMATION - {workflow.harness_type.value.upper()} HARNESS**

**Total Estimated Time:** {workflow.total_estimated_time_minutes} minutes ({workflow.total_estimated_time_minutes/60:.1f} hours)

**Required Machines:** {', '.join(workflow.required_machines) if workflow.required_machines else 'Manual only'}

**Required Operators:**
"""
        for role, count in workflow.required_operators.items():
            response += f"• {role}: {count}\n"
        
        response += "\n**Quality Checkpoints:**\n"
        for cp in workflow.quality_checkpoints:
            response += f"✅ {cp}\n"
        
        response += "\n**Detailed Steps:**\n"
        for step in workflow.steps:
            deps = f" (depends on: {', '.join(step.dependencies)})" if step.dependencies else ""
            machine = f" [Machine: {step.machine_id}]" if step.machine_id else " [Manual]"
            qc = " ✅ QC" if step.quality_check else ""
            response += f"{step.step_id}: {step.name} - {step.estimated_time_minutes} min{machine}{qc}{deps}\n"
            response += f"   Operator: {step.operator_role}\n"
        
        return response
    
    # ==================== MACHINERY RECOMMENDATION ====================
    
    def recommend_machinery(self, requirements: Dict) -> MachineryRecommendation:
        """Recommend machinery based on production requirements"""
        
        harness_type = requirements.get("harness_type", "automotive")
        monthly_volume = requirements.get("monthly_volume", 1000)
        budget = requirements.get("budget", 10000000)  # 1 Cr default
        
        # Filter suitable machines
        suitable_machines = []
        for machine in self.config.machinery:
            if harness_type.lower() in [s.lower() for s in machine["suitable_for"]]:
                suitable_machines.append(machine)
        
        # Sort by price
        suitable_machines.sort(key=lambda m: m["price_inr"])
        
        # Select machines within budget
        selected = []
        total_investment = 0
        for machine in suitable_machines:
            if total_investment + machine["price_inr"] <= budget:
                selected.append(machine)
                total_investment += machine["price_inr"]
        
        # If budget allows, add at least one of each critical type
        critical_types = ["Wire Cutting", "Crimping", "Testing"]
        for ctype in critical_types:
            if not any(ctype.lower() in m["name"].lower() for m in selected):
                for m in suitable_machines:
                    if ctype.lower() in m["name"].lower() and total_investment + m["price_inr"] <= budget * 1.2:
                        selected.append(m)
                        total_investment += m["price_inr"]
                        break
        
        yearly_maintenance = sum(m["maintenance_cost_yearly"] for m in selected)
        power_consumption = sum(m["power_consumption_kw"] for m in selected)
        
        # Estimate production capacity
        # Based on slowest machine speed
        min_speed = min(m["speed"] for m in selected) if selected else 1000
        # Extract numeric speed
        import re
        speed_match = re.search(r'(\d+)', min_speed)
        speed_val = int(speed_match.group(1)) if speed_match else 1000
        # Assume 8 hours/day, 26 days/month, 85% efficiency
        monthly_capacity = speed_val * 8 * 26 * 0.85
        
        # ROI calculation (assuming 18% margin on ₹5000 avg harness)
        avg_revenue_per_unit = 5000
        monthly_revenue = monthly_volume * avg_revenue_per_unit * 0.18
        roi_months = total_investment / monthly_revenue if monthly_revenue > 0 else 0
        
        return MachineryRecommendation(
            recommended_machines=selected,
            total_investment=round(total_investment, 2),
            yearly_maintenance=round(yearly_maintenance, 2),
            power_consumption_kw=round(power_consumption, 1),
            estimated_roi_months=round(roi_months, 1),
            production_capacity_per_month=int(monthly_capacity)
        )
    
    def _format_machinery_recommendation(self, rec: MachineryRecommendation) -> str:
        response = f"""
🤖 **MACHINERY RECOMMENDATION - Segan Industry**

**Total Investment:** ₹{rec.total_investment:,.2f}
**Yearly Maintenance:** ₹{rec.yearly_maintenance:,.2f}
**Power Consumption:** {rec.power_consumption_kw} kW
**Estimated ROI:** {rec.estimated_roi_months:.1f} months
**Monthly Capacity:** {rec.production_capacity_per_month:,} units

**Recommended Machines:**
"""
        for i, machine in enumerate(rec.recommended_machines, 1):
            response += f"""
{i}. **{machine['name']}** ({machine['model']})
   📦 Manufacturer: {machine['manufacturer']}
   ⚡ Capacity: {machine['capacity']} | Speed: {machine['speed']}
   💰 Price: ₹{machine['price_inr']:,.2f}
   🔧 Yearly Maintenance: ₹{machine['maintenance_cost_yearly']:,.2f}
   ⚡ Power: {machine['power_consumption_kw']} kW
   ✅ Suitable for: {', '.join(machine['suitable_for'])}
"""
        return response
    
    def _get_machinery_requirements(self) -> str:
        return """
🤖 **Machinery Recommendation Requirements:**

Please provide:
1. **Harness Type:** automotive / ev / industrial / control_panel
2. **Monthly Production Volume:** Number of harness sets per month
3. **Budget:** Total investment budget in INR
4. **Current Equipment:** Any existing machines?
5. **Space Available:** Floor space in sq ft
6. **Power Supply:** Available power (kW, 3-phase?)

Example: "Recommend machines for 2000 automotive harnesses/month, budget ₹50 lakhs"
"""
    
    # ==================== INVENTORY TRACKING ====================
    
    def check_inventory_status(self) -> List[InventoryStatus]:
        """Check inventory status for all materials"""
        statuses = []
        
        for material_type, material_data in self.materials.items():
            # Simulate current stock (in real implementation, fetch from database)
            import random
            current_stock = random.uniform(
                material_data.get("reorder_point", 100) * 0.5,
                material_data.get("reorder_point", 100) * 2
            )
            
            reorder_point = self.inventory["reorder_points"].get(
                f"{material_type}_{material_data['unit']}", 100
            )
            safety_stock = reorder_point * (self.inventory["safety_stock_days"] / 30)
            
            # Calculate daily consumption (simulated)
            daily_consumption = reorder_point / 30
            days_remaining = int(current_stock / daily_consumption) if daily_consumption > 0 else 999
            
            if current_stock <= safety_stock:
                status = "CRITICAL"
            elif current_stock <= reorder_point:
                status = "LOW"
            else:
                status = "OK"
            
            recommended_qty = max(0, reorder_point * 2 - current_stock)
            
            statuses.append(InventoryStatus(
                material=material_type.replace("_", " ").title(),
                current_stock=round(current_stock, 2),
                unit=material_data["unit"],
                reorder_point=reorder_point,
                safety_stock=round(safety_stock, 2),
                status=status,
                days_remaining=days_remaining,
                recommended_order_qty=round(recommended_qty, 2)
            ))
        
        return statuses
    
    def _format_inventory_status(self, inventory: List[InventoryStatus]) -> str:
        response = """
📦 **INVENTORY STATUS - Segan Industry**

"""
        critical = [i for i in inventory if i.status == "CRITICAL"]
        low = [i for i in inventory if i.status == "LOW"]
        ok = [i for i in inventory if i.status == "OK"]
        
        if critical:
            response += "🔴 **CRITICAL - Immediate Action Required:**\n"
            for item in critical:
                response += f"  • {item.material}: {item.current_stock} {item.unit} (Reorder: {item.reorder_point}, Days left: {item.days_remaining}) - **ORDER {item.recommended_order_qty} {item.unit}**\n"
        
        if low:
            response += "\n🟡 **LOW STOCK - Plan Reorder:**\n"
            for item in low:
                response += f"  • {item.material}: {item.current_stock} {item.unit} (Reorder: {item.reorder_point}, Days left: {item.days_remaining}) - Order {item.recommended_order_qty} {item.unit}\n"
        
        if ok:
            response += "\n🟢 **ADEQUATE STOCK:**\n"
            for item in ok:
                response += f"  • {item.material}: {item.current_stock} {item.unit} (Days left: {item.days_remaining})\n"
        
        response += f"""
---
**Summary:** {len(critical)} Critical | {len(low)} Low | {len(ok)} OK
**Reorder Lead Time Buffer:** {self.config.inventory['lead_time_buffer_days']} days
**Safety Stock:** {self.config.inventory['safety_stock_days']} days
"""
        return response
    
    # ==================== SUPPLIER SELECTION ====================
    
    def get_supplier_recommendations(self, material_type: str) -> List[SupplierInfo]:
        """Get recommended suppliers for a material"""
        material = self.config.materials.get(material_type.lower().replace(" ", "_"))
        if not material:
            return []
        
        suppliers = []
        for sup_id in material["suppliers"]:
            supplier = next((s for s in self.config.suppliers if s["id"] == sup_id), None)
            if supplier:
                suppliers.append(SupplierInfo(**supplier))
        
        # Sort by rating and lead time
        suppliers.sort(key=lambda s: (-s.rating, s.lead_time_days))
        return suppliers
    
    def _format_supplier_recommendations(self, suppliers: List[SupplierInfo]) -> str:
        if not suppliers:
            return "No suppliers found for this material."
        
        response = "🏭 **SUPPLIER RECOMMENDATIONS**\n\n"
        for i, sup in enumerate(suppliers, 1):
            response += f"""
{i}. **{sup.name}** ({sup.location})
   ⭐ Rating: {sup.rating}/5 | ⏱️ Lead Time: {sup.lead_time_days} days | 💳 Terms: {sup.payment_terms}
   📦 Materials: {', '.join(sup.materials)}
   ✅ GST Compliant: {'Yes' if sup.gst_compliant else 'No'}
   Status: {sup.status.title()}
"""
        return response
    
    def _get_all_suppliers_summary(self) -> str:
        response = "🏭 **ALL SUPPLIERS - Segan Industry**\n\n"
        for sup in self.config.suppliers:
            response += f"• **{sup['name']}** ({sup['location']}) - ⭐{sup['rating']} - {sup['lead_time_days']}d lead - {sup['payment_terms']} - {', '.join(sup['materials'])}\n"
        return response
    
    # ==================== AUTOMATION SERVICES ====================
    
    def _get_automation_services(self) -> List[Dict]:
        return [
            {
                "id": "AI_AGENT",
                "name": "AI-Powered Quotation Agent",
                "description": "Automated wiring harness quotation with real-time material pricing, GST calculation, and profit optimization",
                "features": ["Instant quotes", "Material price comparison", "GST compliance", "Profit optimization"],
                "benefits": ["Reduce quote time from hours to minutes", "Eliminate human errors", "Real-time material pricing", "GST compliant quotes"],
                "technologies": ["Python", "FastAPI", "OpenAI", "Real-time pricing APIs"],
                "implementation_time": "2-4 weeks",
                "price_range": "₹2,00,000 - ₹5,00,000"
            },
            {
                "id": "WORKFLOW_AUTO",
                "name": "Production Workflow Automation",
                "description": "Automated production scheduling, work order generation, and progress tracking",
                "features": ["Auto-scheduling", "Resource allocation", "Bottleneck detection", "Real-time tracking"],
                "benefits": ["20-30% productivity increase", "Real-time visibility", "Reduced bottlenecks", "Paperless operations"],
                "technologies": ["IoT sensors", "MES integration", "Dashboard analytics"],
                "implementation_time": "4-8 weeks",
                "price_range": "₹5,00,000 - ₹15,00,000"
            },
            {
                "id": "INVENTORY_AUTO",
                "name": "Smart Inventory Management",
                "description": "AI-driven inventory optimization with predictive reordering and supplier management",
                "features": ["Predictive reordering", "Supplier performance", "Cost optimization", "Stock alerts"],
                "benefits": ["15-25% inventory reduction", "Zero stockouts", "Better supplier terms", "Automated procurement"],
                "technologies": ["ML forecasting", "ERP integration", "Mobile alerts"],
                "implementation_time": "6-10 weeks",
                "price_range": "₹8,00,000 - ₹25,00,000"
            },
            {
                "id": "QUALITY_AUTO",
                "name": "Automated Quality Control",
                "description": "Vision-based inspection and automated testing integration",
                "features": ["AOI integration", "Test data logging", "Traceability", "SPC charts"],
                "benefits": ["100% inspection coverage", "Zero defect escape", "Full traceability", "Regulatory compliance"],
                "technologies": ["Machine vision", "Test equipment integration", "Blockchain traceability"],
                "implementation_time": "8-12 weeks",
                "price_range": "₹15,00,000 - ₹50,00,000"
            }
        ]
    
    def _get_automation_services_info(self) -> str:
        services = self._get_automation_services()
        response = """
🤖 **AUTOMATION SERVICES - Segan Industry**

We offer comprehensive automation solutions for wiring harness manufacturing:

"""
        for svc in services:
            response += f"""
**{svc['name']}**
{svc['description']}

✨ **Features:**
{chr(10).join('• ' + f for f in svc['features'])}

🛠️ **Technologies:** {', '.join(svc['technologies'])}
---
"""
        response += """
**Implementation Approach:**
1. Assessment & Gap Analysis
2. Pilot Project (1 production line)
3. Scale & Integrate
4. Continuous Improvement

**ROI Timeline:** 6-12 months typical
**Investment Range:** ₹10 Lakhs - ₹2 Crores

Contact us for a customized automation roadmap!
"""
        return response
    
    # ==================== COMPANY INFO ====================
    
    def _get_company_info(self) -> str:
        c = self.company
        return f"""
🏢 **SEGAN INDUSTRY PRIVATE LIMITED**

**{c['tagline']}**

📍 **Address:** {c['address']}
📞 **Phone:** {c['phone']}
📧 **Email:** {c['email']}
🌐 **Website:** {c['website']}

**Registrations:**
• GSTIN: {c['gstin']}
• PAN: {c['pan']}
• CIN: {c['cin']}

**Location Advantage:**
• Chennai - India's Automotive Hub (Detroit of India)
• Tamil Nadu - Strong industrial ecosystem
• SIDCO Industrial Estate - Infrastructure ready
• Near major ports (Chennai, Ennore) for export
• Skilled workforce availability
• Proximity to OEMs: Hyundai, Ford, Renault-Nissan, Royal Enfield, TVS, Ashok Leyland

**Core Competencies:**
🔧 Automotive Wiring Harness (2W, 3W, 4W)
⚡ EV & Hybrid Vehicle Harness (High Voltage)
🏭 Industrial & Control Panel Harness
🤖 Factory Automation & AI Integration
📊 Custom Quotation & ERP Solutions

**Certifications Targeted:** IATF 16949, ISO 9001, ISO 14001

*Established 2020 | Chennai, Tamil Nadu, India*
"""
    
    # ==================== HELP ====================
    
    def _get_help_message(self) -> str:
        return """
🤖 **SEGAN INDUSTRY AI AGENT - HELP**

I'm your AI assistant for wiring harness manufacturing. I can help with:

**💰 QUOTATION & PRICING**
• "Generate quotation for 100 automotive harnesses"
• "Compare copper wire prices from suppliers"
• "Calculate GST for ₹5,00,000 invoice"

**📊 FINANCIAL ANALYSIS**
• "Calculate profit/loss for 500 EV harnesses"
• "Show employee cost breakdown"
• "Break-even analysis for new machine"

**🏭 PRODUCTION & OPERATIONS**
• "Show production workflow for EV harness"
• "Recommend machines for 2000 units/month"
• "Check inventory status"

**🏪 SUPPLIER MANAGEMENT**
• "Find best connector suppliers"
• "Compare terminal prices"
• "Supplier performance report"

**🤖 AUTOMATION**
• "What automation services do you offer?"
• "Workflow automation for production"
• "AI quotation integration"

**ℹ️ COMPANY INFO**
• "Tell me about Segan Industry"
• "Contact details for Chennai office"

**GST REFERENCE (Tamil Nadu):**
• Intra-state (TN): CGST 9% + SGST 9% = 18%
• Inter-state: IGST 18%
• HSN 8544 (Wiring Harness), 8536 (Connectors/Terminals)

**Example Queries:**
> "Quote for 200 automotive harnesses, 30m wire, 1mm², 15 connectors, 30 terminals, delivery to Bangalore"
> "Compare PVC wire prices for 5000 meters"
> "P&L for 1000 industrial harnesses monthly"
> "Show production workflow for control panel harness"

How can I assist you today?
"""


# Singleton instance
ai_agent = WiringHarnessAIAgent()


def get_ai_agent() -> WiringHarnessAIAgent:
    """Get the AI agent singleton instance"""
    return ai_agent