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
    },

    # Freelance & Creative Services

    "graphic_designer": {
        "industry_key": "graphic_designer",
        "display_name": "Graphic Designer",
        "recommended_approach": "hourly_or_project",
        "approach_description": "Graphic design is typically priced hourly for ongoing work or flat-rate per project. Many designers offer package pricing for common deliverables (logo, branding, website design).",

        "primary_pricing": {
            "unit": "hourly",
            "base_rate_range": [50, 150],
            "suggested_default": 85,
            "label": "Hourly Rate"
        },

        "additional_rates": [
            {
                "name": "logo_design",
                "label": "Logo Design Package",
                "range": [500, 2500],
                "suggested": 1200,
                "description": "Complete logo design with revisions"
            },
            {
                "name": "branding_package",
                "label": "Brand Identity Package",
                "range": [2000, 8000],
                "suggested": 4000,
                "description": "Full brand identity (logo, colors, typography, guidelines)"
            },
            {
                "name": "rush_fee",
                "label": "Rush Fee",
                "range": [25, 50],
                "suggested": 30,
                "description": "Percentage added for rush projects"
            }
        ],

        "common_project_types": [
            "Logo design",
            "Brand identity package",
            "Marketing materials (flyers, brochures)",
            "Social media graphics",
            "Website design (mockups)",
            "Print design",
            "Packaging design"
        ],

        "pricing_tips": [
            "Package pricing is often more attractive to clients than hourly",
            "Include revision rounds in project quotes (e.g., 2-3 rounds)",
            "Rush projects should command premium rates (25-50% increase)",
            "Consider retainer arrangements for ongoing client work",
            "Price by value delivered, not just time spent",
            "Usage rights matter - commercial use costs more than personal"
        ]
    },

    "web_developer": {
        "industry_key": "web_developer",
        "display_name": "Web Developer",
        "recommended_approach": "hourly_or_project",
        "approach_description": "Web development can be hourly for ongoing work or flat-rate for defined projects. Many developers offer package pricing for common website types.",

        "primary_pricing": {
            "unit": "hourly",
            "base_rate_range": [75, 200],
            "suggested_default": 125,
            "label": "Hourly Rate"
        },

        "additional_rates": [
            {
                "name": "simple_website",
                "label": "Simple Website (5-10 pages)",
                "range": [2500, 8000],
                "suggested": 5000,
                "description": "Basic brochure website"
            },
            {
                "name": "ecommerce_site",
                "label": "E-commerce Website",
                "range": [5000, 20000],
                "suggested": 10000,
                "description": "Full e-commerce site with shopping cart"
            },
            {
                "name": "monthly_maintenance",
                "label": "Monthly Maintenance",
                "range": [100, 500],
                "suggested": 250,
                "description": "Monthly hosting, updates, and support"
            }
        ],

        "common_project_types": [
            "Business website (brochure)",
            "E-commerce website",
            "Custom web application",
            "Website redesign",
            "WordPress site",
            "API development",
            "Monthly maintenance/support"
        ],

        "pricing_tips": [
            "Scope creep is common - define deliverables clearly upfront",
            "Charge separately for design vs development if you do both",
            "Maintenance retainers provide recurring revenue",
            "Hosting and domain management can be additional services",
            "Complex features (user accounts, payment processing) add significant time",
            "Factor in testing time across browsers and devices"
        ]
    },

    "writer": {
        "industry_key": "writer",
        "display_name": "Writer",
        "recommended_approach": "per_word_or_project",
        "approach_description": "Writing is typically priced per word, per article, or per project. Rates vary significantly by content type (blog vs technical writing) and expertise level.",

        "primary_pricing": {
            "unit": "per_word",
            "base_rate_range": [0.10, 1.00],
            "suggested_default": 0.30,
            "label": "Per Word Rate"
        },

        "additional_rates": [
            {
                "name": "blog_post",
                "label": "Blog Post (800-1200 words)",
                "range": [150, 600],
                "suggested": 300,
                "description": "Standard blog article"
            },
            {
                "name": "technical_writing",
                "label": "Technical Writing (per hour)",
                "range": [75, 150],
                "suggested": 100,
                "description": "Technical documentation, whitepapers"
            },
            {
                "name": "copywriting",
                "label": "Sales Copy (per project)",
                "range": [500, 3000],
                "suggested": 1200,
                "description": "Website copy, landing pages, sales pages"
            }
        ],

        "common_project_types": [
            "Blog posts and articles",
            "Website copy",
            "Technical documentation",
            "Email marketing campaigns",
            "Social media content",
            "Whitepapers and ebooks",
            "Product descriptions"
        ],

        "pricing_tips": [
            "Per-word pricing works for straightforward content",
            "Complex topics (technical, medical, legal) command higher rates",
            "Include research time in project-based pricing",
            "Charge extra for SEO optimization and keyword research",
            "Rush projects should be 25-50% higher",
            "Unlimited revisions can kill profitability - cap revision rounds"
        ]
    },

    "photographer": {
        "industry_key": "photographer",
        "display_name": "Photographer",
        "recommended_approach": "per_event_or_session",
        "approach_description": "Photography is typically priced per session/event with packages that include a set number of edited photos. Additional photos, prints, and albums are upsells.",

        "primary_pricing": {
            "unit": "per_session",
            "base_rate_range": [200, 800],
            "suggested_default": 400,
            "label": "Standard Session (1-2 hours)"
        },

        "additional_rates": [
            {
                "name": "wedding_full_day",
                "label": "Wedding Photography (full day)",
                "range": [2000, 6000],
                "suggested": 3500,
                "description": "8-10 hour wedding coverage"
            },
            {
                "name": "commercial_hourly",
                "label": "Commercial (per hour)",
                "range": [150, 500],
                "suggested": 250,
                "description": "Product, real estate, commercial photography"
            },
            {
                "name": "additional_photos",
                "label": "Additional Edited Photos",
                "range": [15, 50],
                "suggested": 25,
                "description": "Per additional edited photo beyond package"
            }
        ],

        "common_project_types": [
            "Portrait session",
            "Wedding photography",
            "Event photography",
            "Real estate photography",
            "Product photography",
            "Headshots",
            "Family photos"
        ],

        "pricing_tips": [
            "Package pricing (session + X edited photos) simplifies client decisions",
            "Post-processing time is significant - factor into pricing",
            "Travel fees for locations beyond X miles",
            "Weddings are premium work - full day coverage commands top rates",
            "Rights and licensing matter - commercial use costs more",
            "Prints and albums are high-margin add-ons"
        ]
    },

    "videographer": {
        "industry_key": "videographer",
        "display_name": "Videographer",
        "recommended_approach": "per_project_or_day",
        "approach_description": "Videography is typically priced per project or day rate. Pricing includes filming and editing. Complex projects (weddings, commercials) are bid as packages.",

        "primary_pricing": {
            "unit": "per_day",
            "base_rate_range": [500, 2500],
            "suggested_default": 1200,
            "label": "Day Rate (filming)"
        },

        "additional_rates": [
            {
                "name": "editing_hourly",
                "label": "Video Editing (per hour)",
                "range": [75, 150],
                "suggested": 100,
                "description": "Post-production editing rate"
            },
            {
                "name": "wedding_package",
                "label": "Wedding Video Package",
                "range": [2500, 8000],
                "suggested": 4500,
                "description": "Full day filming + edited highlight video"
            },
            {
                "name": "commercial_project",
                "label": "Commercial Video (30-60 sec)",
                "range": [3000, 15000],
                "suggested": 7000,
                "description": "Scripted commercial video production"
            }
        ],

        "common_project_types": [
            "Wedding videography",
            "Corporate video",
            "Commercial/ad production",
            "Event coverage",
            "Real estate video tours",
            "Social media video content",
            "Documentary projects"
        ],

        "pricing_tips": [
            "Day rate should cover equipment costs and travel",
            "Editing takes 3-5x filming time - price accordingly",
            "Multi-camera shoots increase complexity and cost",
            "Drone footage is a premium add-on",
            "Rights and usage matter - broadcast vs web vs internal use",
            "Revisions beyond 2 rounds should cost extra"
        ]
    },

    # Event Services

    "dj": {
        "industry_key": "dj",
        "display_name": "DJ",
        "recommended_approach": "per_event",
        "approach_description": "DJ services are typically priced per event with packages based on event length. Weddings and corporate events command premium rates over private parties.",

        "primary_pricing": {
            "unit": "per_event",
            "base_rate_range": [400, 1500],
            "suggested_default": 800,
            "label": "Standard Event (4 hours)"
        },

        "additional_rates": [
            {
                "name": "wedding_package",
                "label": "Wedding Package (6-8 hours)",
                "range": [1200, 3000],
                "suggested": 1800,
                "description": "Wedding reception with MC services"
            },
            {
                "name": "additional_hour",
                "label": "Additional Hour",
                "range": [100, 250],
                "suggested": 150,
                "description": "Per additional hour beyond package"
            },
            {
                "name": "lighting_upgrade",
                "label": "Lighting Package",
                "range": [200, 800],
                "suggested": 400,
                "description": "Uplighting, dance floor lighting, etc."
            }
        ],

        "common_project_types": [
            "Wedding reception",
            "Corporate event",
            "Birthday party",
            "School dance",
            "Club/bar residency",
            "Festival performance",
            "Private party"
        ],

        "pricing_tips": [
            "Weddings are premium - include MC services and planning time",
            "Travel fees for events beyond X miles",
            "Lighting and photo booth are high-margin add-ons",
            "Overtime should be priced in contract (rate per additional hour)",
            "Corporate events often have higher budgets than private parties",
            "Equipment quality matters - invest in professional gear"
        ]
    },

    "caterer": {
        "industry_key": "caterer",
        "display_name": "Caterer",
        "recommended_approach": "per_person",
        "approach_description": "Catering is typically priced per person with menu packages. Additional fees for service staff, equipment rental, and travel. Full-service catering includes setup and cleanup.",

        "primary_pricing": {
            "unit": "per_person",
            "base_rate_range": [15, 100],
            "suggested_default": 35,
            "label": "Per Person (standard menu)"
        },

        "additional_rates": [
            {
                "name": "premium_menu",
                "label": "Premium Menu (per person)",
                "range": [50, 150],
                "suggested": 75,
                "description": "Upscale menu with premium ingredients"
            },
            {
                "name": "service_staff",
                "label": "Service Staff (per server per hour)",
                "range": [25, 50],
                "suggested": 35,
                "description": "Waitstaff, bartenders, etc."
            },
            {
                "name": "equipment_rental",
                "label": "Equipment/Rental Fee",
                "range": [200, 1000],
                "suggested": 500,
                "description": "Tables, chairs, linens, serving equipment"
            }
        ],

        "common_project_types": [
            "Wedding catering",
            "Corporate event",
            "Birthday party",
            "Holiday party",
            "Graduation party",
            "Rehearsal dinner",
            "Drop-off catering (no service)"
        ],

        "pricing_tips": [
            "Menu pricing should include food cost + labor + overhead + profit",
            "Service staff should be priced separately from food",
            "Minimum guest counts ensure profitability (e.g., 25-50 minimum)",
            "Travel and delivery fees for events outside your area",
            "Rentals can be marked up or passed through at cost",
            "Tastings for large events can be charged (credited if they book)"
        ]
    },

    "event_planner": {
        "industry_key": "event_planner",
        "display_name": "Event Planner",
        "recommended_approach": "percentage_or_flat",
        "approach_description": "Event planning is priced as a percentage of total event budget (10-20%) or flat fee per event. Full-service planning costs more than day-of coordination.",

        "primary_pricing": {
            "unit": "percentage",
            "base_rate_range": [10, 20],
            "suggested_default": 15,
            "label": "Planning Fee (% of budget)"
        },

        "additional_rates": [
            {
                "name": "full_planning",
                "label": "Full Planning (flat fee)",
                "range": [3000, 15000],
                "suggested": 7500,
                "description": "Complete planning from start to finish"
            },
            {
                "name": "day_of_coordination",
                "label": "Day-of Coordination",
                "range": [800, 2500],
                "suggested": 1500,
                "description": "Coordination on event day only"
            },
            {
                "name": "hourly_consulting",
                "label": "Hourly Consulting",
                "range": [75, 200],
                "suggested": 125,
                "description": "A la carte planning advice"
            }
        ],

        "common_project_types": [
            "Wedding planning (full service)",
            "Wedding day-of coordination",
            "Corporate event planning",
            "Birthday party planning",
            "Nonprofit fundraiser",
            "Product launch event",
            "Conference planning"
        ],

        "pricing_tips": [
            "Percentage pricing scales with event size and complexity",
            "Full planning (6-12 months) costs more than partial planning",
            "Day-of coordination is lower commitment, good entry service",
            "Flat fees work better than percentage for small events",
            "Include planning hours in proposal (meetings, vendor coordination, etc.)",
            "Travel costs for site visits should be separate or built in"
        ]
    },

    "florist": {
        "industry_key": "florist",
        "display_name": "Florist",
        "recommended_approach": "per_arrangement_or_package",
        "approach_description": "Floral design is priced per arrangement or as event packages. Wedding and event work is typically bid as complete packages after consultation.",

        "primary_pricing": {
            "unit": "per_arrangement",
            "base_rate_range": [50, 200],
            "suggested_default": 100,
            "label": "Standard Arrangement"
        },

        "additional_rates": [
            {
                "name": "bridal_bouquet",
                "label": "Bridal Bouquet",
                "range": [150, 400],
                "suggested": 250,
                "description": "Wedding bridal bouquet"
            },
            {
                "name": "wedding_package",
                "label": "Wedding Floral Package",
                "range": [1500, 8000],
                "suggested": 3500,
                "description": "Complete wedding florals (bouquets, centerpieces, ceremony)"
            },
            {
                "name": "delivery_setup",
                "label": "Delivery & Setup",
                "range": [50, 200],
                "suggested": 100,
                "description": "Delivery and on-site setup"
            }
        ],

        "common_project_types": [
            "Wedding florals",
            "Event centerpieces",
            "Funeral arrangements",
            "Birthday/celebration arrangements",
            "Corporate arrangements",
            "Bridal bouquets",
            "Corsages and boutonnieres"
        ],

        "pricing_tips": [
            "Flower costs vary by season - price accordingly",
            "Labor-intensive designs (cascading bouquets, installations) cost more",
            "Delivery and setup are separate charges",
            "Wedding consultations should be thorough - build trust",
            "Markup on flowers is typically 2.5-3x wholesale cost",
            "Premium flowers (peonies, garden roses) command higher prices"
        ]
    },

    "wedding_coordinator": {
        "industry_key": "wedding_coordinator",
        "display_name": "Wedding Coordinator",
        "recommended_approach": "flat_fee_or_percentage",
        "approach_description": "Wedding coordination is priced as flat fee or percentage of total wedding budget. Full planning (12+ months) costs more than partial planning or day-of coordination.",

        "primary_pricing": {
            "unit": "flat_fee",
            "base_rate_range": [2000, 10000],
            "suggested_default": 5000,
            "label": "Full Wedding Planning"
        },

        "additional_rates": [
            {
                "name": "partial_planning",
                "label": "Partial Planning (3-6 months)",
                "range": [1500, 5000],
                "suggested": 2500,
                "description": "Planning starting 3-6 months before wedding"
            },
            {
                "name": "day_of_coordination",
                "label": "Day-of Coordination",
                "range": [1000, 3000],
                "suggested": 1800,
                "description": "Coordination on wedding day only"
            },
            {
                "name": "rehearsal_coordination",
                "label": "Rehearsal Coordination",
                "range": [200, 500],
                "suggested": 300,
                "description": "Rehearsal dinner coordination"
            }
        ],

        "common_project_types": [
            "Full wedding planning (12+ months)",
            "Partial wedding planning (3-6 months)",
            "Day-of coordination",
            "Destination wedding planning",
            "Elopement planning",
            "Rehearsal dinner coordination",
            "Vendor coordination"
        ],

        "pricing_tips": [
            "Full planning includes unlimited meetings and vendor sourcing",
            "Partial planning is for couples who want help finishing details",
            "Day-of coordination ensures smooth execution (rehearsal + wedding day)",
            "Destination weddings command premium due to travel and complexity",
            "Include vendor communication hours in pricing",
            "Travel costs should be separate for out-of-town weddings"
        ]
    },

    # Personal Services

    "personal_trainer": {
        "industry_key": "personal_trainer",
        "display_name": "Personal Trainer",
        "recommended_approach": "per_session_or_package",
        "approach_description": "Personal training is priced per session or as package deals (e.g., 10-session pack). Group training and online coaching are additional revenue streams.",

        "primary_pricing": {
            "unit": "per_session",
            "base_rate_range": [50, 150],
            "suggested_default": 80,
            "label": "1-on-1 Session (60 min)"
        },

        "additional_rates": [
            {
                "name": "session_package",
                "label": "10-Session Package",
                "range": [450, 1200],
                "suggested": 700,
                "description": "Package of 10 sessions (discounted)"
            },
            {
                "name": "group_training",
                "label": "Group Training (per person)",
                "range": [25, 50],
                "suggested": 35,
                "description": "Small group training (3-6 people)"
            },
            {
                "name": "online_coaching",
                "label": "Online Coaching (monthly)",
                "range": [100, 400],
                "suggested": 200,
                "description": "Monthly online training program"
            }
        ],

        "common_project_types": [
            "1-on-1 personal training",
            "Session packages (5, 10, 20 sessions)",
            "Small group training",
            "Online coaching programs",
            "Nutrition coaching add-on",
            "Corporate wellness programs",
            "Athletic performance training"
        ],

        "pricing_tips": [
            "Package pricing encourages commitment and reduces no-shows",
            "Session packages should offer discount vs single session rate",
            "Group training is more affordable per person but profitable for you",
            "Online coaching provides passive income with lower time commitment",
            "Specializations (sports performance, rehab) command higher rates",
            "Cancellation policy is critical - charge for late cancellations"
        ]
    },

    "tutor": {
        "industry_key": "tutor",
        "display_name": "Tutor",
        "recommended_approach": "hourly_or_package",
        "approach_description": "Tutoring is typically priced hourly with discounts for package deals. Rates vary by subject difficulty and grade level (test prep and college-level tutoring cost more).",

        "primary_pricing": {
            "unit": "hourly",
            "base_rate_range": [30, 100],
            "suggested_default": 50,
            "label": "Hourly Rate (K-12)"
        },

        "additional_rates": [
            {
                "name": "test_prep",
                "label": "Test Prep (SAT/ACT/GRE)",
                "range": [75, 200],
                "suggested": 125,
                "description": "Standardized test preparation"
            },
            {
                "name": "college_level",
                "label": "College-Level Tutoring",
                "range": [60, 150],
                "suggested": 85,
                "description": "College coursework tutoring"
            },
            {
                "name": "package_discount",
                "label": "10-Hour Package",
                "range": [270, 900],
                "suggested": 450,
                "description": "Package of 10 hours (10% discount)"
            }
        ],

        "common_project_types": [
            "K-12 homework help",
            "SAT/ACT test prep",
            "College essay coaching",
            "Math tutoring",
            "Language tutoring",
            "College-level coursework",
            "Study skills coaching"
        ],

        "pricing_tips": [
            "Test prep commands premium rates due to specialized knowledge",
            "Advanced subjects (calculus, organic chemistry) justify higher rates",
            "Package deals (10-20 hours) encourage commitment",
            "Online tutoring can expand your market beyond local area",
            "Cancellation policy needed - charge for late cancellations",
            "Group tutoring (2-3 students) is profitable middle ground"
        ]
    },

    "coach": {
        "industry_key": "coach",
        "display_name": "Coach",
        "recommended_approach": "per_session_or_package",
        "approach_description": "Coaching (life, business, executive) is priced per session or as monthly retainers. Package deals (3-6 months) are common. Group coaching programs provide leverage.",

        "primary_pricing": {
            "unit": "per_session",
            "base_rate_range": [100, 500],
            "suggested_default": 200,
            "label": "1-on-1 Session (60 min)"
        },

        "additional_rates": [
            {
                "name": "monthly_retainer",
                "label": "Monthly Retainer (4 sessions)",
                "range": [400, 2000],
                "suggested": 800,
                "description": "Monthly coaching package"
            },
            {
                "name": "vip_day",
                "label": "VIP Day (6-8 hours)",
                "range": [1500, 5000],
                "suggested": 2500,
                "description": "Intensive one-day session"
            },
            {
                "name": "group_program",
                "label": "Group Coaching Program (per person)",
                "range": [500, 3000],
                "suggested": 1200,
                "description": "6-12 week group coaching program"
            }
        ],

        "common_project_types": [
            "1-on-1 coaching sessions",
            "Monthly retainer packages",
            "VIP intensive days",
            "Group coaching programs",
            "Corporate executive coaching",
            "Career transition coaching",
            "Business coaching"
        ],

        "pricing_tips": [
            "Package deals (3-6 months) ensure client commitment and results",
            "Monthly retainers provide predictable recurring revenue",
            "VIP days command premium pricing for concentrated value",
            "Group programs provide leverage (coach many at once)",
            "Specialization (executive, business, leadership) commands higher rates",
            "Online delivery expands market beyond local geography"
        ]
    },

    "consultant": {
        "industry_key": "consultant",
        "display_name": "Consultant",
        "recommended_approach": "hourly_or_project",
        "approach_description": "Consulting is priced hourly or per project depending on scope. Retainer arrangements provide ongoing advisory services. Rate varies widely by expertise and industry.",

        "primary_pricing": {
            "unit": "hourly",
            "base_rate_range": [100, 500],
            "suggested_default": 200,
            "label": "Hourly Consulting Rate"
        },

        "additional_rates": [
            {
                "name": "project_based",
                "label": "Project Fee (typical)",
                "range": [5000, 50000],
                "suggested": 15000,
                "description": "Fixed-price project engagement"
            },
            {
                "name": "monthly_retainer",
                "label": "Monthly Retainer",
                "range": [2000, 20000],
                "suggested": 5000,
                "description": "Ongoing advisory services"
            },
            {
                "name": "workshop_training",
                "label": "Workshop/Training (per day)",
                "range": [2000, 10000],
                "suggested": 5000,
                "description": "On-site workshop or training session"
            }
        ],

        "common_project_types": [
            "Strategy consulting",
            "Process improvement",
            "Technology implementation",
            "Change management",
            "Business advisory",
            "Workshop facilitation",
            "Executive advisory"
        ],

        "pricing_tips": [
            "Value-based pricing often works better than hourly for projects",
            "Retainers provide predictable revenue and client access",
            "Project-based pricing reduces client sticker shock vs hourly",
            "Workshops and training are high-value deliverables",
            "Scope definition is critical - avoid scope creep",
            "Implementation work can be priced separately from strategy"
        ]
    },

    "music_teacher": {
        "industry_key": "music_teacher",
        "display_name": "Music Teacher",
        "recommended_approach": "per_lesson_or_monthly",
        "approach_description": "Music lessons are priced per lesson or as monthly packages (e.g., 4 lessons/month). Group lessons cost less per student. Online lessons expand market reach.",

        "primary_pricing": {
            "unit": "per_lesson",
            "base_rate_range": [30, 80],
            "suggested_default": 50,
            "label": "Private Lesson (30 min)"
        },

        "additional_rates": [
            {
                "name": "hour_lesson",
                "label": "Private Lesson (60 min)",
                "range": [50, 120],
                "suggested": 75,
                "description": "One-hour private lesson"
            },
            {
                "name": "monthly_package",
                "label": "Monthly Package (4 lessons)",
                "range": [120, 320],
                "suggested": 200,
                "description": "Four weekly lessons per month"
            },
            {
                "name": "group_lesson",
                "label": "Group Lesson (per student)",
                "range": [20, 40],
                "suggested": 30,
                "description": "Group lesson (3-6 students)"
            }
        ],

        "common_project_types": [
            "Private lessons (piano, guitar, voice, etc.)",
            "Group lessons",
            "Online lessons (Zoom)",
            "Recital preparation",
            "Music theory instruction",
            "Beginner to advanced levels",
            "Summer intensives"
        ],

        "pricing_tips": [
            "Monthly packages encourage commitment vs pay-per-lesson",
            "60-minute lessons should cost more than 2x 30-minute rate",
            "Advanced students and exam prep can justify higher rates",
            "Group lessons are profitable but require more coordination",
            "Online lessons expand your geographic market",
            "Cancellation policy critical - charge for late cancellations",
            "Recital fees can be separate to cover venue costs"
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
