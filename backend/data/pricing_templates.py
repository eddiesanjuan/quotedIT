"""
Pricing templates for different industries.

Provides recommended pricing approaches, rate ranges, and guidance
for contractors setting up their pricing in Quoted.
"""

PRICING_TEMPLATES = {
    "electrician": {
        "industry_key": "electrician",
        "display_name": "Electrician",
        "recommended_approach": "hourly_plus_materials",
        "approach_description": "Charge hourly for labor with material markup. Service calls typically have a minimum charge that covers travel time.",

        "primary_pricing": {
            "unit": "hourly",
            "base_rate_range": [75, 150],
            "suggested_default": 95,
            "label": "Hourly Labor Rate"
        },

        "additional_rates": [
            {
                "name": "service_call_minimum",
                "label": "Minimum Service Call",
                "range": [85, 150],
                "suggested": 125,
                "description": "Minimum charge for any service call (covers travel time and diagnostics)"
            },
            {
                "name": "material_markup",
                "label": "Material Markup %",
                "range": [15, 35],
                "suggested": 20,
                "description": "Percentage added to material costs"
            },
            {
                "name": "emergency_rate",
                "label": "Emergency/After-Hours Rate",
                "range": [125, 225],
                "suggested": 150,
                "description": "Hourly rate for emergency or after-hours calls"
            }
        ],

        "common_project_types": [
            "Service call / troubleshooting",
            "Outlet or switch installation",
            "Circuit breaker panel upgrade",
            "Whole-house rewiring",
            "Lighting fixture installation",
            "Ceiling fan installation",
            "Generator hookup"
        ],

        "pricing_tips": [
            "Service calls should have a minimum to cover travel time and basic diagnostics",
            "Complex jobs (panels, rewiring) are often quoted flat-rate after an inspection",
            "Material markup covers sourcing time, warranty, and overhead",
            "Emergency/after-hours work should command premium rates (1.5-2x normal)"
        ]
    },

    "plumber": {
        "industry_key": "plumber",
        "display_name": "Plumber",
        "recommended_approach": "hourly_plus_materials",
        "approach_description": "Hourly labor rate with material markup. Service calls have a diagnostic fee that's often credited toward repair work.",

        "primary_pricing": {
            "unit": "hourly",
            "base_rate_range": [85, 175],
            "suggested_default": 125,
            "label": "Hourly Labor Rate"
        },

        "additional_rates": [
            {
                "name": "service_call_minimum",
                "label": "Diagnostic/Service Call Fee",
                "range": [100, 200],
                "suggested": 150,
                "description": "Diagnostic fee (typically credited if customer proceeds with repair)"
            },
            {
                "name": "material_markup",
                "label": "Material Markup %",
                "range": [20, 40],
                "suggested": 25,
                "description": "Percentage added to parts and materials"
            },
            {
                "name": "emergency_rate",
                "label": "Emergency/After-Hours Rate",
                "range": [150, 275],
                "suggested": 200,
                "description": "Rate for emergency calls and weekend work"
            }
        ],

        "common_project_types": [
            "Service call / leak repair",
            "Toilet installation or repair",
            "Sink or faucet installation",
            "Water heater installation",
            "Drain cleaning",
            "Pipe repair or replacement",
            "Sewer line work"
        ],

        "pricing_tips": [
            "Diagnostic fees should cover your time to identify the problem",
            "Common practice is to credit the diagnostic fee if customer proceeds with repair",
            "Emergency plumbing (burst pipes, sewage backups) commands premium rates",
            "Consider flat-rate pricing for common jobs (toilet install, water heater, etc.)",
            "Material markup should account for trips to supply house and warranty"
        ]
    },

    "hvac": {
        "industry_key": "hvac",
        "display_name": "HVAC",
        "recommended_approach": "mixed",
        "approach_description": "Service calls are typically hourly or flat diagnostic fee. System installations are usually flat-rate bids. Maintenance contracts are monthly/annual.",

        "primary_pricing": {
            "unit": "hourly",
            "base_rate_range": [85, 150],
            "suggested_default": 110,
            "label": "Hourly Service Rate"
        },

        "additional_rates": [
            {
                "name": "diagnostic_fee",
                "label": "Diagnostic Fee",
                "range": [89, 150],
                "suggested": 125,
                "description": "Fee for diagnosing AC/heating issues"
            },
            {
                "name": "maintenance_contract",
                "label": "Annual Maintenance Contract",
                "range": [200, 350],
                "suggested": 250,
                "description": "Yearly maintenance plan (2 visits: spring & fall)"
            },
            {
                "name": "emergency_rate",
                "label": "Emergency Rate",
                "range": [125, 225],
                "suggested": 165,
                "description": "After-hours or emergency service rate"
            }
        ],

        "common_project_types": [
            "AC repair/service call",
            "Furnace repair/service call",
            "Central AC system installation",
            "Furnace installation",
            "Duct work installation or repair",
            "Thermostat installation",
            "Annual maintenance contract"
        ],

        "pricing_tips": [
            "System installations (AC, furnace) are typically flat-rate after site visit",
            "Service calls can be hourly or diagnostic fee (often credited toward repair)",
            "Maintenance contracts provide predictable recurring revenue",
            "Emergency calls (no heat in winter, no AC in summer) command premium rates",
            "Consider seasonal pricing adjustments for peak demand periods"
        ]
    },

    "roofer": {
        "industry_key": "roofer",
        "display_name": "Roofer",
        "recommended_approach": "per_square",
        "approach_description": "Roofing is typically priced per 'square' (100 sq ft). Full replacements are bid as flat-rate projects. Repairs can be hourly or flat-rate.",

        "primary_pricing": {
            "unit": "per_square",
            "base_rate_range": [350, 650],
            "suggested_default": 450,
            "label": "Price per Square (100 sq ft)"
        },

        "additional_rates": [
            {
                "name": "tear_off_per_square",
                "label": "Tear-Off per Square",
                "range": [100, 200],
                "suggested": 150,
                "description": "Cost to remove existing roofing (per square)"
            },
            {
                "name": "inspection_fee",
                "label": "Roof Inspection",
                "range": [150, 300],
                "suggested": 200,
                "description": "Fee for detailed roof inspection and report"
            },
            {
                "name": "emergency_repair",
                "label": "Emergency Repair Minimum",
                "range": [400, 800],
                "suggested": 500,
                "description": "Minimum charge for emergency leak repairs"
            }
        ],

        "common_project_types": [
            "Full roof replacement (asphalt shingles)",
            "Roof repair (leak, storm damage)",
            "Tear-off and replacement",
            "Roof inspection",
            "Flashing repair",
            "Gutter installation",
            "Emergency tarp/temporary repair"
        ],

        "pricing_tips": [
            "One square = 100 sq ft. Typical house is 15-30 squares.",
            "Price per square varies by material (asphalt vs metal vs tile)",
            "Tear-off adds cost - price it separately or include in total",
            "Steep pitches and multiple stories add complexity and cost",
            "Emergency repairs (active leaks) can command premium rates",
            "Inspections should be thorough and provide value (detailed report with photos)"
        ]
    },

    "cabinet_maker": {
        "industry_key": "cabinet_maker",
        "display_name": "Cabinet Maker",
        "recommended_approach": "per_linear_foot",
        "approach_description": "Custom cabinets are typically priced per linear foot. Projects are usually bid as flat-rate after measuring and design consultation.",

        "primary_pricing": {
            "unit": "per_linear_foot",
            "base_rate_range": [400, 800],
            "suggested_default": 500,
            "label": "Custom Cabinets (per linear foot)"
        },

        "additional_rates": [
            {
                "name": "design_fee",
                "label": "Design Consultation",
                "range": [200, 500],
                "suggested": 300,
                "description": "Fee for design and measurement (often credited toward project)"
            },
            {
                "name": "refacing_per_lf",
                "label": "Cabinet Refacing (per LF)",
                "range": [100, 250],
                "suggested": 150,
                "description": "Price to reface existing cabinets"
            },
            {
                "name": "countertop_per_sqft",
                "label": "Countertop Installation (per sq ft)",
                "range": [50, 150],
                "suggested": 75,
                "description": "Countertop fabrication and installation"
            }
        ],

        "common_project_types": [
            "Custom kitchen cabinets",
            "Bathroom vanity cabinets",
            "Built-in shelving/entertainment center",
            "Cabinet refacing",
            "Countertop installation",
            "Cabinet repair or modification"
        ],

        "pricing_tips": [
            "Linear foot pricing varies significantly by materials (plywood vs solid wood)",
            "Design fees should be substantial - credit toward project if they commit",
            "Factor in hardware, hinges, drawer slides, and finishing",
            "Complex designs (crown molding, glass doors, specialty finishes) add cost",
            "Countertops are often sold separately - price per sq ft by material type",
            "Lead times can be long - be clear about scheduling in quotes"
        ]
    },

    "general_contractor": {
        "industry_key": "general_contractor",
        "display_name": "General Contractor",
        "recommended_approach": "percentage_markup",
        "approach_description": "GCs typically charge a percentage of total project cost (10-20%) or cost-plus markup. Large projects are bid as fixed-price contracts.",

        "primary_pricing": {
            "unit": "percentage",
            "base_rate_range": [10, 20],
            "suggested_default": 15,
            "label": "Project Management Fee (%)"
        },

        "additional_rates": [
            {
                "name": "consultation_fee",
                "label": "Initial Consultation",
                "range": [150, 300],
                "suggested": 200,
                "description": "Fee for project assessment and initial estimate"
            },
            {
                "name": "hourly_rate",
                "label": "Hourly Rate (small jobs)",
                "range": [75, 150],
                "suggested": 95,
                "description": "Hourly rate for small repair/handyman work"
            },
            {
                "name": "remodel_per_sqft",
                "label": "Remodel Estimate (per sq ft)",
                "range": [100, 250],
                "suggested": 150,
                "description": "Rough ballpark for renovation projects"
            }
        ],

        "common_project_types": [
            "Kitchen remodel",
            "Bathroom remodel",
            "Home addition",
            "Whole-house renovation",
            "Basement finishing",
            "New construction",
            "Commercial tenant improvement"
        ],

        "pricing_tips": [
            "Project management fee (10-20%) covers coordination, permits, scheduling",
            "Fixed-price contracts shift risk to you - estimate carefully with contingency",
            "Cost-plus contracts (cost + % markup) are safer but less appealing to clients",
            "Consultation fees should be meaningful - shows your expertise has value",
            "Per-square-foot estimates are rough - always do detailed takeoffs for actual bids",
            "Include allowances for client selections (fixtures, finishes) in contracts"
        ]
    },

    "painter": {
        "industry_key": "painter",
        "display_name": "Painter",
        "recommended_approach": "per_square_foot",
        "approach_description": "Interior painting is typically priced per square foot or by room. Exterior by square foot or flat-rate per house. Cabinet painting is per linear foot.",

        "primary_pricing": {
            "unit": "per_sqft",
            "base_rate_range": [2.50, 5.00],
            "suggested_default": 3.50,
            "label": "Interior Painting (per sq ft)"
        },

        "additional_rates": [
            {
                "name": "exterior_per_sqft",
                "label": "Exterior Painting (per sq ft)",
                "range": [3.50, 6.00],
                "suggested": 4.50,
                "description": "Exterior house painting rate"
            },
            {
                "name": "cabinet_per_lf",
                "label": "Cabinet Painting (per LF)",
                "range": [60, 100],
                "suggested": 75,
                "description": "Kitchen cabinet refinishing"
            },
            {
                "name": "minimum_job",
                "label": "Minimum Job",
                "range": [300, 600],
                "suggested": 400,
                "description": "Minimum charge for any painting job"
            }
        ],

        "common_project_types": [
            "Interior room painting",
            "Whole house interior",
            "Exterior house painting",
            "Kitchen cabinet refinishing",
            "Trim and door painting",
            "Ceiling painting",
            "Deck or fence staining"
        ],

        "pricing_tips": [
            "Prep work (sanding, patching, priming) can double the time - price accordingly",
            "High ceilings, intricate trim, and textured walls increase difficulty",
            "Cabinet painting is premium work - charge accordingly (it's detail-intensive)",
            "Exterior work depends on house height, surface condition, and weather windows",
            "Paint quality matters - specify if your price includes premium paint vs basic",
            "Minimum job charge ensures small jobs are profitable"
        ]
    },

    "flooring": {
        "industry_key": "flooring",
        "display_name": "Flooring Installer",
        "recommended_approach": "per_square_foot",
        "approach_description": "Flooring is priced per square foot for both materials and labor. Installation rates vary by material type (hardwood, tile, vinyl, carpet).",

        "primary_pricing": {
            "unit": "per_sqft",
            "base_rate_range": [6.00, 15.00],
            "suggested_default": 10.00,
            "label": "Installation Labor (per sq ft)"
        },

        "additional_rates": [
            {
                "name": "hardwood_install",
                "label": "Hardwood Install (per sq ft)",
                "range": [8, 18],
                "suggested": 12,
                "description": "Hardwood floor installation"
            },
            {
                "name": "tile_install",
                "label": "Tile Install (per sq ft)",
                "range": [10, 25],
                "suggested": 15,
                "description": "Ceramic or porcelain tile installation"
            },
            {
                "name": "removal_per_sqft",
                "label": "Flooring Removal (per sq ft)",
                "range": [2, 5],
                "suggested": 3,
                "description": "Removal of existing flooring"
            }
        ],

        "common_project_types": [
            "Hardwood floor installation",
            "Vinyl plank flooring (LVP)",
            "Tile floor installation",
            "Carpet installation",
            "Floor refinishing (hardwood)",
            "Subfloor repair",
            "Transition strips and trim"
        ],

        "pricing_tips": [
            "Installation rate varies by material - tile is more labor-intensive than vinyl",
            "Removal and disposal of old flooring should be priced separately",
            "Subfloor condition affects job difficulty - assess and price accordingly",
            "Complex patterns, diagonal layouts, or intricate cuts increase labor",
            "Material waste (10-15%) should be factored into material quotes",
            "Moving furniture can be an upcharge or included - be clear in quote"
        ]
    },

    "concrete": {
        "industry_key": "concrete",
        "display_name": "Concrete Contractor",
        "recommended_approach": "per_square_foot",
        "approach_description": "Concrete work is typically priced per square foot for flatwork (driveways, patios) or per linear foot for foundations. Decorative concrete commands premium rates.",

        "primary_pricing": {
            "unit": "per_sqft",
            "base_rate_range": [6.00, 12.00],
            "suggested_default": 8.00,
            "label": "Concrete Flatwork (per sq ft)"
        },

        "additional_rates": [
            {
                "name": "stamped_concrete",
                "label": "Stamped/Decorative (per sq ft)",
                "range": [15, 25],
                "suggested": 18,
                "description": "Stamped or decorative concrete"
            },
            {
                "name": "foundation_per_lf",
                "label": "Foundation (per LF)",
                "range": [125, 200],
                "suggested": 150,
                "description": "Foundation walls (per linear foot)"
            },
            {
                "name": "removal_per_sqft",
                "label": "Concrete Removal (per sq ft)",
                "range": [3, 7],
                "suggested": 5,
                "description": "Removal and disposal of existing concrete"
            }
        ],

        "common_project_types": [
            "Driveway pour",
            "Patio or walkway",
            "Foundation walls",
            "Garage floor",
            "Stamped concrete patio",
            "Concrete steps",
            "Curb and gutter"
        ],

        "pricing_tips": [
            "Thickness matters - 4-inch vs 6-inch slab affects material and cost",
            "Site access and prep (excavation, gravel base) can double the job cost",
            "Decorative work (stamping, coloring, exposed aggregate) commands premium",
            "Removal of existing concrete is labor-intensive - price accordingly",
            "Weather can delay pours - build flexibility into schedule",
            "Finishing quality (smooth trowel vs broom finish) affects labor"
        ]
    },

    "deck_builder": {
        "industry_key": "deck_builder",
        "display_name": "Deck Builder",
        "recommended_approach": "per_square_foot",
        "approach_description": "Deck building is priced per square foot. Rate varies significantly by material (pressure-treated wood vs composite). Railings priced per linear foot.",

        "primary_pricing": {
            "unit": "per_sqft",
            "base_rate_range": [35, 70],
            "suggested_default": 50,
            "label": "Deck Construction (per sq ft)"
        },

        "additional_rates": [
            {
                "name": "composite_deck",
                "label": "Composite Deck (per sq ft)",
                "range": [45, 75],
                "suggested": 55,
                "description": "Composite decking (Trex, TimberTech, etc.)"
            },
            {
                "name": "railing_per_lf",
                "label": "Railing (per LF)",
                "range": [30, 50],
                "suggested": 35,
                "description": "Deck railing installation"
            },
            {
                "name": "demolition",
                "label": "Deck Removal",
                "range": [600, 1500],
                "suggested": 800,
                "description": "Removal and disposal of existing deck"
            }
        ],

        "common_project_types": [
            "New deck construction (wood)",
            "New deck construction (composite)",
            "Deck repair or replacement boards",
            "Railing installation",
            "Deck demolition",
            "Stairs and landing",
            "Deck staining or sealing"
        ],

        "pricing_tips": [
            "Composite costs more than wood but less maintenance - educate clients",
            "Ground-level decks are simpler than elevated decks (less structural work)",
            "Railing is separate from deck surface - price per linear foot",
            "Stairs and landings are complex - price as separate line items",
            "Permits and inspections required in most areas - factor into bid",
            "Demo and disposal of old deck should be priced separately"
        ]
    },

    "landscaper": {
        "industry_key": "landscaper",
        "display_name": "Landscaper",
        "recommended_approach": "mixed",
        "approach_description": "Landscaping combines design fees, per-square-foot pricing for planting/sod, and project-based pricing for hardscaping. Maintenance is typically monthly contracts.",

        "primary_pricing": {
            "unit": "hourly",
            "base_rate_range": [50, 100],
            "suggested_default": 65,
            "label": "Hourly Labor Rate"
        },

        "additional_rates": [
            {
                "name": "design_fee",
                "label": "Landscape Design",
                "range": [300, 1000],
                "suggested": 500,
                "description": "Design consultation and plan (often credited)"
            },
            {
                "name": "sod_per_sqft",
                "label": "Sod Installation (per sq ft)",
                "range": [1.50, 3.50],
                "suggested": 2.00,
                "description": "Sod installation including prep"
            },
            {
                "name": "monthly_maintenance",
                "label": "Monthly Maintenance",
                "range": [150, 400],
                "suggested": 250,
                "description": "Monthly lawn and landscape maintenance"
            }
        ],

        "common_project_types": [
            "Landscape design and installation",
            "Sod or seeding",
            "Planting beds and shrubs",
            "Hardscape (pavers, retaining walls)",
            "Irrigation system install",
            "Mulch and edging",
            "Monthly maintenance contract"
        ],

        "pricing_tips": [
            "Design fees should reflect expertise - credit toward install if they proceed",
            "Material costs vary widely - plants, stone, pavers - markup 20-40%",
            "Hardscaping (pavers, walls) is significantly more than softscaping (plants)",
            "Monthly maintenance contracts provide steady recurring revenue",
            "Irrigation installs are specialized - price separately from planting",
            "Prep work (grading, soil amendment) can be as much as plant cost"
        ]
    },

    "handyman": {
        "industry_key": "handyman",
        "display_name": "Handyman",
        "recommended_approach": "hourly",
        "approach_description": "Handyman work is typically hourly with a minimum charge (often 2-hour minimum). Some jobs may be bid flat-rate based on scope.",

        "primary_pricing": {
            "unit": "hourly",
            "base_rate_range": [50, 95],
            "suggested_default": 65,
            "label": "Hourly Rate"
        },

        "additional_rates": [
            {
                "name": "minimum_charge",
                "label": "Minimum Charge",
                "range": [100, 200],
                "suggested": 130,
                "description": "Minimum charge (typically 2 hours)"
            },
            {
                "name": "material_markup",
                "label": "Material Markup %",
                "range": [15, 30],
                "suggested": 20,
                "description": "Markup on materials purchased"
            }
        ],

        "common_project_types": [
            "Small repairs and odd jobs",
            "Furniture assembly",
            "Door and lock installation",
            "Drywall repair and patching",
            "Painting touch-ups",
            "Minor plumbing repairs",
            "Deck or fence repair"
        ],

        "pricing_tips": [
            "2-hour minimum ensures small jobs are profitable",
            "Be clear if travel time is included or charged separately",
            "Material markup should cover trips to hardware store",
            "Build trust by providing free estimates for jobs over $500",
            "Consider flat-rate pricing for common tasks (door install, ceiling fan, etc.)",
            "Efficiency is key - don't overbid on jobs you can do quickly"
        ]
    },

    "tile": {
        "industry_key": "tile",
        "display_name": "Tile Installer",
        "recommended_approach": "per_square_foot",
        "approach_description": "Tile work is priced per square foot for floors/walls. Showers and complex patterns command higher rates. Includes prep, installation, and grouting.",

        "primary_pricing": {
            "unit": "per_sqft",
            "base_rate_range": [10, 25],
            "suggested_default": 15,
            "label": "Tile Installation (per sq ft)"
        },

        "additional_rates": [
            {
                "name": "shower_install",
                "label": "Shower Install (flat rate)",
                "range": [2000, 4000],
                "suggested": 2500,
                "description": "Full tile shower installation"
            },
            {
                "name": "backsplash_per_sqft",
                "label": "Backsplash (per sq ft)",
                "range": [12, 30],
                "suggested": 18,
                "description": "Kitchen backsplash tile"
            },
            {
                "name": "removal_per_sqft",
                "label": "Tile Removal (per sq ft)",
                "range": [3, 7],
                "suggested": 5,
                "description": "Removal of existing tile"
            }
        ],

        "common_project_types": [
            "Bathroom floor tile",
            "Kitchen backsplash",
            "Shower tile installation",
            "Floor tile installation",
            "Tile repair or replacement",
            "Grout and caulk refresh"
        ],

        "pricing_tips": [
            "Small tiles (mosaics, penny tiles) take longer - charge more per sq ft",
            "Complex patterns (herringbone, chevron) increase labor significantly",
            "Showers are premium work - waterproofing and precision are critical",
            "Tile removal is dusty, labor-intensive work - don't undercharge",
            "Substrate condition affects job - assess floor flatness before quoting",
            "Include materials (thinset, grout, spacers) in quote or price separately"
        ]
    },

    "drywall": {
        "industry_key": "drywall",
        "display_name": "Drywall Contractor",
        "recommended_approach": "per_square_foot",
        "approach_description": "Drywall is priced per square foot for hanging, taping, and finishing. Can be broken into stages (hang, tape, texture) or priced as complete.",

        "primary_pricing": {
            "unit": "per_sqft",
            "base_rate_range": [2.50, 5.00],
            "suggested_default": 3.50,
            "label": "Complete Drywall (per sq ft)"
        },

        "additional_rates": [
            {
                "name": "hang_only",
                "label": "Hang Only (per sq ft)",
                "range": [1.00, 2.00],
                "suggested": 1.50,
                "description": "Hanging drywall only (no taping)"
            },
            {
                "name": "tape_only",
                "label": "Tape/Finish (per sq ft)",
                "range": [0.50, 1.25],
                "suggested": 0.75,
                "description": "Taping and finishing only"
            },
            {
                "name": "texture_per_sqft",
                "label": "Texture (per sq ft)",
                "range": [0.40, 1.00],
                "suggested": 0.50,
                "description": "Texture application (knockdown, orange peel)"
            }
        ],

        "common_project_types": [
            "New construction drywall",
            "Room addition drywall",
            "Ceiling drywall",
            "Drywall repair/patches",
            "Basement drywall",
            "Garage drywall"
        ],

        "pricing_tips": [
            "Complete pricing (hang, tape, texture) is simpler for clients to understand",
            "High ceilings and hard-to-reach areas increase difficulty and cost",
            "Level 5 finish (smooth, no texture) is premium work - charge accordingly",
            "Repairs can be hourly or flat-rate depending on size",
            "Material costs (drywall, mud, tape, corner bead) should be separate line item",
            "Scaffolding or special equipment for high work should be factored in"
        ]
    },

    "window_door": {
        "industry_key": "window_door",
        "display_name": "Window & Door Installer",
        "recommended_approach": "per_unit",
        "approach_description": "Window and door installation is priced per unit. Price varies by type (window vs door, standard vs custom). Materials often sold separately from labor.",

        "primary_pricing": {
            "unit": "per_unit",
            "base_rate_range": [350, 700],
            "suggested_default": 450,
            "label": "Window Install (per unit)"
        },

        "additional_rates": [
            {
                "name": "door_install",
                "label": "Door Install (per unit)",
                "range": [400, 800],
                "suggested": 500,
                "description": "Interior or exterior door installation"
            },
            {
                "name": "sliding_door",
                "label": "Sliding Door (per unit)",
                "range": [600, 1200],
                "suggested": 800,
                "description": "Patio or sliding door installation"
            },
            {
                "name": "trim_per_unit",
                "label": "Trim/Casing (per unit)",
                "range": [75, 150],
                "suggested": 100,
                "description": "Interior trim and casing"
            }
        ],

        "common_project_types": [
            "Window replacement",
            "Exterior door installation",
            "Interior door installation",
            "Sliding glass door install",
            "Storm door installation",
            "Trim and casing"
        ],

        "pricing_tips": [
            "Custom sizes and shapes cost more than standard windows",
            "Old window removal and disposal should be priced separately or included",
            "Exterior work requires weatherproofing - don't underestimate time",
            "Structural issues (rot, improper rough opening) can add cost - inspect first",
            "Trim and casing can be significant labor - price separately or include",
            "Material markup if you're sourcing windows/doors (or customer provides)"
        ]
    }
}


def get_template(industry_key: str) -> dict:
    """Get pricing template for a specific industry."""
    return PRICING_TEMPLATES.get(industry_key)


def list_all_templates() -> list:
    """List all available templates with basic info."""
    return [
        {
            "key": template["industry_key"],
            "name": template["display_name"]
        }
        for template in PRICING_TEMPLATES.values()
    ]
