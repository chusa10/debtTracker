# helpers.py

def format_currency(value):
    """Format a numeric value as currency, e.g. 1234.5 -> '$1,234.50'."""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)


def parse_number(text):
    """Convert a string like '$1,234.50' into a float 1234.5."""
    s = str(text).replace("$", "").replace(",", "").strip()
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def compute_percentage(line_val, bal_val):
    """Return utilization percentage = balance / line_of_credit * 100."""
    if line_val:
        return round((bal_val / line_val) * 100, 2)
    return ""


def format_percentage_display(percentage):
    """Return '57.3%' style text for the percentage column."""
    if percentage == "" or percentage is None:
        return ""
    try:
        p = float(percentage)
    except (ValueError, TypeError):
        return str(percentage)
    return f"{p:.1f}%"


def get_percentage_tag(percentage):
    """Return 'high_util' only if percentage > 50."""
    try:
        p = float(percentage)
    except (ValueError, TypeError):
        return ""
    return "high_util" if p >= 50 else ""
