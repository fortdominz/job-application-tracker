# models.py - Application Model
# This file defines what an "application" looks like in our tracker.
# Think of it like a form - it lists all the fields and checks they're filled in correctly.

from datetime import datetime

# These are the allowed job types a user can choose from
JOB_TYPES = [
    "Internship",
    "Full-Time",
    "Part-Time",
    "Co-op",
    "Contract",
]

# These are the only valid statuses an application can have.
# The order here represents the typical pipeline from start to finish.
STATUSES = [
    "Saved",             # You've bookmarked it but haven't applied yet
    "Applied",           # You submitted the application
    "Online Assessment", # You received a coding test or quiz
    "Phone Screen",      # A recruiter reached out for a quick call
    "Interview",         # You're in the interview stage
    "Final Round",       # Last round of interviews
    "Offer",             # You got an offer!
    "Rejected",          # They passed on your application
    "Withdrawn",         # You decided to withdraw your application
]


def create_application(company, role, location, source,
                        status="Saved", job_type="Internship",
                        date_applied=None, deadline=None,
                        salary=None, notes=None):
    # This function builds a new application dictionary after checking the inputs.
    # It raises a ValueError if something is wrong, which we catch in main.py.

    # Clean up any accidental extra spaces
    company = company.strip()
    role = role.strip()

    # These two fields are required - everything else is optional
    if company == "":
        raise ValueError("Company name cannot be empty.")
    if role == "":
        raise ValueError("Role cannot be empty.")

    # Make sure the status is one of the allowed values
    if status not in STATUSES:
        raise ValueError(f"'{status}' is not a valid status. Choose from: {', '.join(STATUSES)}")

    # Job type can be one of the standard options OR a custom value the user typed in
    # We just make sure it isn't blank
    if not job_type or job_type.strip() == "":
        raise ValueError("Job type cannot be empty.")

    # If dates were provided, make sure they're in the right format
    if date_applied:
        check_date_format(date_applied, "date_applied")
    if deadline:
        check_date_format(deadline, "deadline")

    # Build and return the application as a dictionary
    application = {
        "company":      company,
        "role":         role,
        "job_type":     job_type,
        "location":     location.strip() if location else "",
        "source":       source.strip() if source else "",
        "status":       status,
        "date_applied": date_applied if date_applied else "",
        "deadline":     deadline if deadline else "",
        "salary":       salary.strip() if salary else "",
        "notes":        notes.strip() if notes else "",
    }

    return application


def check_date_format(date_string, field_name):
    # Dates must be in YYYY-MM-DD format, e.g. 2025-06-01
    # strptime will throw an error if the format doesn't match
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"'{field_name}' must be in YYYY-MM-DD format. Example: 2025-06-01")
