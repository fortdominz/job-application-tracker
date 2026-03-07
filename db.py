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
