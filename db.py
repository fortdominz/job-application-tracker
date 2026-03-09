# db.py - Database Helper
# This file is responsible for saving and loading applications.
# We're using a simple JSON file as our "database" for now.
# In the future, we can swap this out for MongoDB - only this file needs to change!

import json
import os
from datetime import datetime

# This is the name of the file where we store all our applications
DATA_FILE = "applications.json"


# ── Loading and Saving ────────────────────────────────────────────────────────

def load_applications():
    # If the file doesn't exist yet, just return an empty list
    if not os.path.exists(DATA_FILE):
        return []

    # Open the file and read the JSON data into a Python list
    with open(DATA_FILE, "r") as file:
        applications = json.load(file)

    return applications


def save_applications(applications):
    # Write the full list of applications back to the file
    # indent=2 makes the file human-readable if you open it in a text editor
    with open(DATA_FILE, "w") as file:
        json.dump(applications, file, indent=2)


# ── ID Generation ─────────────────────────────────────────────────────────────

def get_next_id(applications):
    # If there are no applications yet, start IDs at 1
    if len(applications) == 0:
        return 1

    # Otherwise, find the highest existing ID and add 1
    highest_id = 0
    for app in applications:
        if app["id"] > highest_id:
            highest_id = app["id"]

    return highest_id + 1


# ── CRUD Operations ───────────────────────────────────────────────────────────
# CRUD = Create, Read, Update, Delete - the four basic things you do with data

def get_all_applications():
    # Simply load and return everything
    return load_applications()


def get_application_by_id(app_id):
    applications = load_applications()

    # Loop through and find the one that matches the ID
    for app in applications:
        if app["id"] == app_id:
            return app

    # If we never found it, return None (meaning "nothing found")
    return None


def add_application(new_app):
    applications = load_applications()

    # Assign a unique ID and record when it was created
    new_app["id"] = get_next_id(applications)
    new_app["date_created"] = datetime.now().isoformat()
    new_app["last_updated"] = datetime.now().isoformat()

    # Add to the list and save
    applications.append(new_app)
    save_applications(applications)

    return new_app


def update_application(app_id, updated_fields):
    applications = load_applications()

    for app in applications:
        if app["id"] == app_id:
            # Update only the fields that were passed in
            for key, value in updated_fields.items():
                app[key] = value

            # Record when the update happened
            app["last_updated"] = datetime.now().isoformat()

            save_applications(applications)
            return app

    # If no application was found with that ID, return None
    return None


def delete_application(app_id):
    applications = load_applications()

    # Build a new list that excludes the application we want to delete
    updated_list = []
    found = False

    for app in applications:
        if app["id"] == app_id:
            found = True  # We found it, so we skip adding it to the new list
        else:
            updated_list.append(app)

    if found:
        save_applications(updated_list)

    # Return True if we deleted something, False if the ID didn't exist
    return found


def filter_applications(status=None, company=None):
    applications = load_applications()
    results = []

    for app in applications:
        # Check if this app matches the filters
        # If a filter is None, we skip that check (treat it as "any")
        status_matches  = (status  is None) or (app.get("status",  "").lower() == status.lower())
        company_matches = (company is None) or (company.lower() in app.get("company", "").lower())

        if status_matches and company_matches:
            results.append(app)

    return results


# ── Sorting ───────────────────────────────────────────────────────────────────

def sort_applications(applications, sort_by):
    # Returns a sorted copy of the applications list.
    # We never modify the original list — we sort a copy and return it.
    # sort_by must be one of: "id", "deadline", "date_applied", "company", "status"

    from models import STATUSES

    if sort_by == "id":
        # Default order — the order they were added
        return sorted(applications, key=lambda app: app["id"])

    elif sort_by == "deadline":
        # Soonest deadline first. Applications with no deadline go to the bottom.
        # We use "9999-99-99" as a fallback so blank deadlines sort last.
        return sorted(applications, key=lambda app: app.get("deadline", "") or "9999-99-99")

    elif sort_by == "date_applied":
        # Most recently applied first. Applications with no date go to the bottom.
        return sorted(applications, key=lambda app: app.get("date_applied", "") or "9999-99-99", reverse=True)

    elif sort_by == "company":
        # Alphabetical by company name, case-insensitive
        return sorted(applications, key=lambda app: app.get("company", "").lower())

    elif sort_by == "status":
        # Pipeline order — Saved first, Withdrawn last.
        # We look up each status's position in the STATUSES list.
        # If somehow the status isn't in the list, it goes to the end.
        def status_order(app):
            status = app.get("status", "")
            return STATUSES.index(status) if status in STATUSES else len(STATUSES)
        return sorted(applications, key=status_order)

    # If an unrecognised sort_by value was passed, return as-is
    return applications


# ── Keyword Search ────────────────────────────────────────────────────────────

def search_applications(keyword):
    # Searches across every text field of every application.
    # Returns any application where the keyword appears anywhere — case-insensitive.
    # For example, searching "google" would match:
    #   - company: "Google"
    #   - notes: "Referred by someone at Google"
    #   - source: "Google Jobs"

    if not keyword or keyword.strip() == "":
        return []

    keyword_lower = keyword.strip().lower()

    # These are all the fields we search through
    searchable_fields = [
        "company", "role", "job_type", "location",
        "source", "status", "salary", "notes",
        "deadline", "date_applied",
    ]

    matches = []

    for app in load_applications():
        # Check every searchable field to see if the keyword appears in it
        for field in searchable_fields:
            field_value = str(app.get(field, "")).lower()

            if keyword_lower in field_value:
                matches.append(app)
                break  # No need to check more fields once we find a match

    return matches
