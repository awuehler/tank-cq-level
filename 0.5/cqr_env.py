# TODO:
#   - Extend to include +1 vendor support
#   - Refactor

# ----------------------------------------------------------------------
# Optimize for local runtime environment ...
PUMP_FEATURE = ["3.5 GPM", "45 PSI"]            # Seed values pump
TANK_FEATURE = ["3.0 GAL", "12 INCH"]           # Seed values tank
TIME_CHECKED = ["37.29", "61"]                  # Intervals (seconds)
BOOL_OUTPUTS = [TRUE]                           # Extra Stdout (debug)
PDUS_SMARTLY = ["DWL", 
    "192.168.XXX.YYY", 
    "userX", "passY", 
    "outlet", "protocol"
    ]                                           # PDU Vendor
# ----------------------------------------------------------------------
