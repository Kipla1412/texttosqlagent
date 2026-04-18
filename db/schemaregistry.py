from typing import Dict, List


class SchemaRegistry:

    # PATIENT DOMAIN
    PATIENT_SCHEMA: Dict[str, Dict] = {
        
        "patient": {
            "description": (
                "This table stores core demographic and identity information about patients. "
                "Each row represents a unique patient. "
                "Use this table when querying patient names, gender, status, or general profile details."
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary Key (PK). Internal identifier used for joins."
                },
                "patient_id": {
                    "type": "VARCHAR", 
                    "description": "External identifier. DO NOT use for joins. Always use 'id' for joins."
                },
                "given_name": {
                    "type": "VARCHAR",
                    "description": "First name of the patient."
                },
                "family_name": {
                    "type": "VARCHAR", 
                    "description": "Last name of the patient."
                },
                "gender": {
                    "type": "VARCHAR",
                    "description": "Gender of the patient (male, female, other)."
                },
                "birth_date": {
                    "type": "DATE",
                    "description": "Date of birth of the patient."
                },
                "active": {
                    "type": "BOOLEAN",
                    "description": "Indicates if patient is active."
                },
                "deceased_boolean": {
                    "type": "BOOLEAN",
                    "description": "Indicates if patient is deceased."
                }
            },
            "join_hint": "Use patient.id for joins with other tables",
            "role": "Primary table for all joins",
            "query_hint": "Start from this table for patient-related queries"
        },

        "patient_identifier": {
            "description": (
                "This table stores external identifiers for patients such as Aadhar, Passport, or Insurance IDs. "
                "Each patient can have multiple identifiers."
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key for the identifier record."
                },
                "patient_id": {
                    "type": "INTEGER",
                    "description": "Foreign key referencing patient.id. Used to link identifiers to a patient."
                },
                "system": {
                    "type": "VARCHAR",
                    "description": "Type of identifier (e.g., 'Aadhar', 'Passport', 'Insurance')."
                },
                "value": {
                    "type": "VARCHAR",
                    "description": "Actual identifier value assigned to the patient."
                },
            },
            "join_hint": "Join using patient_identifier.patient_id = patient.id",
        },

        "patient_telecom": {
            "description": (
                "Stores patient contact information such as phone numbers and email addresses.\n"
                "Each patient can have multiple contact methods.\n"
                "Use cases:\n"
                "- Get patient phone numbers\n"
                "- Retrieve email addresses"
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary Key (PK). Unique telecom record."
                },
                "patient_id": {
                    "type": "INTEGER",
                    "description": "Foreign Key (FK) -> patient.id. Used for joins."
                },
                "system": {
                    "type": "VARCHAR",
                    "description": "Contact type: phone, email, sms."
                },
                "value": {
                    "type": "VARCHAR",
                    "description": "Actual contact value."
                },
                "use": {
                    "type": "VARCHAR",
                    "description": "Usage type: home, work, mobile."
                }
            },
            "join_hint": "patient.id = patient_telecom.patient_id",
            "relationship": "One patient can have multiple telecom records (1:N)",
            "query_hint": "Join with patient to fetch contact details"
        },

        "patient_address": {
            "description": (
                "Stores address details of patients.\n"
                "Each patient can have one or more addresses.\n"
                "Use cases:\n"
                "- Get patient address\n"
                "- Filter patients by city or state"
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary Key (PK). Unique address record."
                },
                "patient_id": {
                    "type": "INTEGER",
                    "description": "Foreign Key (FK) -> patient.id. Used for joins."
                },
                "line": {
                    "type": "VARCHAR",
                    "description": "Street address or house details."
                },
                "city": {
                    "type": "VARCHAR",
                    "description": "City where the patient resides."
                },
                "state": {
                    "type": "VARCHAR",
                    "description": "State or region of the patient."
                },
                "postal_code": {
                    "type": "VARCHAR",
                    "description": "ZIP or postal code."
                },
                "country": {
                    "type": "VARCHAR",
                    "description": "Country of residence."
                }
            },
            "join_hint": "patient.id = patient_address.patient_id",
            "relationship": "One patient can have multiple addresses (1:N)",
            "query_hint": "Join with patient to retrieve address details"
        },
    }

    # PATIENT DOMAIN
    PATIENT_RELATIONSHIPS = [
        "patient JOIN patient_identifier ON patient.id = patient_identifier.patient_id",
        "patient JOIN patient_telecom ON patient.id = patient_telecom.patient_id",
        "patient JOIN patient_address ON patient.id = patient_address.patient_id",
    ]

    # PRACTITIONER DOMAIN
    PRACTITIONER_SCHEMA: Dict[str, Dict] = {

        "practitioner": {
            "description": (
                "Stores healthcare professionals such as doctors, nurses, and specialists. "
                "Each row represents one practitioner."
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary Key (PK). Internal identifier used for joins."
                },
                "practitioner_id": {
                    "type": "VARCHAR",
                    "description": "External public ID. DO NOT use for joins."
                },
                "user_id": {
                    "type": "INTEGER",
                    "description": "User reference ID."
                },
                "org_id": {
                    "type": "INTEGER",
                    "description": "Organization ID."
                },
                "active": {
                    "type": "BOOLEAN",
                    "description": "Indicates if practitioner is active."
                },
                "given_name": {
                    "type": "VARCHAR",
                    "description": "First name of practitioner."
                },
                "family_name": {
                    "type": "VARCHAR",
                    "description": "Last name of practitioner."
                },
                "gender": {
                    "type": "VARCHAR",
                    "description": "Gender of practitioner."
                },
                "birth_date": {
                    "type": "DATE",
                    "description": "Date of birth."
                },
                "role": {
                    "type": "VARCHAR",
                    "description": "Role (doctor, nurse, specialist)."
                },
                "specialty": {
                    "type": "VARCHAR",
                    "description": "Medical specialty."
                },
                "deceased_boolean": {
                    "type": "BOOLEAN",
                    "description": "Whether practitioner is deceased."
                },
                "deceased_datetime": {
                    "type": "TIMESTAMP",
                    "description": "Date/time of death."
                },
                "created_at": {
                    "type": "TIMESTAMP",
                    "description": "Record creation timestamp."
                },
                "updated_at": {
                    "type": "TIMESTAMP",
                    "description": "Last updated timestamp."
                }
            },
            "join_hint": "Use practitioner.id for joins",
            "role": "Primary table for practitioner queries",
            "query_hint": "Start from this table for doctor/practitioner queries",
        },

        "practitioner_identifier": {
                "description": (
                    "Stores external identifiers for practitioners such as license numbers, "
                    "registration IDs, or certifications."
                ),
                "columns": {
                    "id": {
                        "type": "INTEGER",
                        "description": "Primary key."
                    },
                    "practitioner_id": {
                        "type": "INTEGER",
                        "description": "Foreign Key (FK) -> practitioner.id"
                    },
                    "org_id": {
                        "type": "INTEGER",
                        "description": "Organization ID."
                    },
                    "system": {
                        "type": "VARCHAR",
                        "description": "Type of identifier (license, registration)."
                    },
                    "value": {
                        "type": "VARCHAR",
                        "description": "Identifier value."
                    },
                    "use": {
                        "type": "VARCHAR",
                        "description": "Usage type."
                    },
                },
                "join_hint": "practitioner.id = practitioner_identifier.practitioner_id",
                "relationship": "One practitioner can have multiple identifiers (1:N)",
            },

        "practitioner_telecom": {
            "description": (
                "Stores practitioner contact details such as phone numbers and email addresses."
            ),
            "columns": {
                "id": "Primary key.",
                "practitioner_id": "Foreign Key (FK) → practitioner.id",
                "org_id": "Organization ID.",
                "system": "Contact type (phone, email).",
                "value": "Contact value.",
                "use": "Usage type (work, home).",
                "rank": "Priority order of contact.",
            },
            "join_hint": "practitioner.id = practitioner_telecom.practitioner_id",
            "relationship": "One practitioner can have multiple telecom entries (1:N)",
        },

        "practitioner_address": {
            "description": (
                "Stores practitioner address details including location and postal information."
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key."
                },
                "practitioner_id": {
                    "type": "INTEGER",
                    "description": "Foreign Key (FK) → practitioner.id"
                },
                "org_id": {
                    "type": "INTEGER",
                    "description": "Organization ID."
                },
                "use": {
                    "type": "VARCHAR",
                    "description": "Address usage type."
                },
                "type": {
                    "type": "VARCHAR",
                    "description": "Address type."
                },
                "text": {
                    "type": "VARCHAR",
                    "description": "Full address text."
                },
                "line": {
                    "type": "VARCHAR",
                    "description": "Street address."
                },
                "city": {
                    "type": "VARCHAR",
                    "description": "City."
                },
                "district": {
                    "type": "VARCHAR",
                    "description": "District."
                },
                "state": {
                    "type": "VARCHAR",
                    "description": "State."
                },
                "postal_code": {
                    "type": "VARCHAR",
                    "description": "ZIP or postal code."
                },
                "country": {
                    "type": "VARCHAR",
                    "description": "Country."
                },
            },
            "join_hint": "practitioner.id = practitioner_address.practitioner_id",
            "relationship": "One practitioner can have multiple addresses (1:N)",
        },

        "practitioner_qualification": {
            "description": (
                "Stores practitioner qualifications such as degrees, certifications, and issuing organizations."
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key."
                },
                "practitioner_id": {
                    "type": "INTEGER",
                    "description": "Foreign Key (FK) → practitioner.id"
                },
                "org_id": {
                    "type": "INTEGER",
                    "description": "Organization ID."
                },
                "identifier_system": {
                    "type": "VARCHAR",
                    "description": "Qualification identifier system."
                },
                "identifier_value": {
                    "type": "VARCHAR",
                    "description": "Qualification identifier value."
                },
                "code_text": {
                    "type": "VARCHAR",
                    "description": "Qualification (MD, PhD, etc)."
                },
                "issuer": {
                    "type": "VARCHAR",
                    "description": "Organization issuing the qualification."
                },
            },
            "join_hint": "practitioner.id = practitioner_qualification.practitioner_id",
            "relationship": "One practitioner can have multiple qualifications (1:N)",
        },
    }

    PRACTITIONER_RELATIONSHIPS = [
        "practitioner JOIN practitioner_identifier ON practitioner.id = practitioner_identifier.practitioner_id",
        "practitioner JOIN practitioner_telecom ON practitioner.id = practitioner_telecom.practitioner_id",
        "practitioner JOIN practitioner_address ON practitioner.id = practitioner_address.practitioner_id",
        "practitioner JOIN practitioner_qualification ON practitioner.id = practitioner_qualification.practitioner_id",
    ]

    ENCOUNTER_SCHEMA = {

        "encounter": {
            "description": (
                "Represents a patient visit or interaction with healthcare providers. "
                "Each row represents one encounter (visit/consultation)."
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary Key (PK). Internal ID used for joins."
                },
                "encounter_id": {
                    "type": "VARCHAR",
                    "description": "External public ID. DO NOT use for joins."
                },
                "user_id": {
                    "type": "INTEGER",
                    "description": "User reference ID."
                },
                "org_id": {
                    "type": "INTEGER",
                    "description": "Organization ID."
                },
                "status": {
                    "type": "VARCHAR",
                    "description": "Encounter status (planned, in-progress, finished, cancelled)."
                },
                "class_code": {
                    "type": "VARCHAR",
                    "description": "Type of encounter (inpatient, outpatient, emergency)."
                },
                "priority": {
                    "type": "VARCHAR",
                    "description": "Priority level."
                },
                "subject_type": {
                    "type": "VARCHAR",
                    "description": "Type of subject (patient)."
                },
                "subject_id": {
                    "type": "INTEGER",
                    "description": "Reference ID → patient.id"
                },
                "subject_display": {
                    "type": "VARCHAR",
                    "description": "Display name of subject."
                },
                "period_start": {
                    "type": "TIMESTAMP",
                    "description": "Start time of encounter."
                },
                "period_end": {
                    "type": "TIMESTAMP",
                    "description": "End time of encounter."
                },
                "created_at": {
                    "type": "TIMESTAMP",
                    "description": "Creation timestamp."
                },
                "updated_at": {
                    "type": "TIMESTAMP",
                    "description": "Last updated timestamp."
                },
            },
            "join_hint": (
                "Use encounter.subject_id = patient.id for patient joins"
            ),
            "role": "Core table connecting patient and healthcare events",
            "query_hint": "Use for visit history, consultations, and treatment tracking",
        },

        "encounter_participant": {
            "description": (
                "Stores participants involved in an encounter, such as doctors or practitioners."
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key."
                },
                "encounter_id": {
                    "type": "INTEGER",
                    "description": "FK → encounter.id"
                },
                "org_id": {
                    "type": "INTEGER",
                    "description": "Organization ID."
                },
                "type_text": {
                    "type": "VARCHAR",
                    "description": "Role (Primary Physician, Consultant)."
                },
                "reference_type": {
                    "type": "VARCHAR",
                    "description": "Type of participant (practitioner)."
                },
                "individual_reference": {
                    "type": "INTEGER",
                    "description": "Reference ID → practitioner.id"
                },
                "period_start": {
                    "type": "TIMESTAMP",
                    "description": "Participation start time."
                },
                "period_end": {
                    "type": "TIMESTAMP",
                    "description": "Participation end time."
                },
            },
            "join_hint": (
                "encounter.id = encounter_participant.encounter_id "
                "AND encounter_participant.individual_reference = practitioner.id"
            ),
            "relationship": "One encounter can have multiple participants (1:N)",
        },

        "encounter_type": {
            "description": "Stores type classification of encounter",
            "columns": {
                "id": "Primary key",
                "encounter_id": "FK → encounter.id",
                "coding_system": "Coding system",
                "coding_code": "Code",
                "coding_display": "Display text",
                "text": "Description",
            },
            "join_hint": "encounter.id = encounter_type.encounter_id",
        },

        "encounter_diagnosis": {
            "description": "Stores diagnoses associated with encounter",
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key"
                },
                "encounter_id": {
                    "type": "INTEGER",
                    "description": "FK → encounter.id"
                },
                "condition_reference": {
                    "type": "VARCHAR",
                    "description": "Reference to condition"
                },
                "use_text": {
                    "type": "VARCHAR",
                    "description": "Usage (admission, discharge)"
                },
                "rank": {
                    "type": "INTEGER",
                    "description": "Priority rank"
                },
            },
            "join_hint": "encounter.id = encounter_diagnosis.encounter_id",
        },

        "encounter_location": {
            "description": "Stores location details for encounter",
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key"
                },
                "encounter_id": {
                    "type": "INTEGER",
                    "description": "FK → encounter.id"
                },
                "location_reference": {
                    "type": "VARCHAR",
                    "description": "Location reference"
                },
                "status": {
                    "type": "VARCHAR",
                    "description": "Location status"
                },
                "period_start": {
                    "type": "TIMESTAMP",
                    "description": "Start time"
                },
                "period_end": {
                    "type": "TIMESTAMP",
                    "description": "End time"
                },
            },
            "join_hint": "encounter.id = encounter_location.encounter_id",
        },

        "encounter_reason_code": {
            "description": "Stores reasons for encounter",
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key"
                },
                "encounter_id": {
                    "type": "INTEGER",
                    "description": "FK → encounter.id"
                },
                "coding_system": {
                    "type": "VARCHAR",
                    "description": "Code system"
                },
                "coding_code": {
                    "type": "VARCHAR",
                    "description": "Code"
                },
                "coding_display": {
                    "type": "VARCHAR",
                    "description": "Display"
                },
                "text": {
                    "type": "VARCHAR",
                    "description": "Reason description"
                },
            },
            "join_hint": "encounter.id = encounter_reason_code.encounter_id",
        },

        "based_on": {
            "description": (
                "Links an encounter to the resource that initiated it, such as an appointment, "
                "service request, or referral.\n\n"
                
                "IMPORTANT:\n"
                "- This is a polymorphic reference table\n"
                "- 'reference_type' determines which table to join\n"
                "- 'reference_id' stores the ID of the referenced record\n\n"

                "JOIN RULES:\n"
                "- If reference_type = 'appointment' → join appointment.id\n"
                "- If reference_type = 'service_request' → join service_request.id\n"
                "- Always join encounter first, then resolve reference dynamically"
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key."
                },
                "encounter_id": {
                    "type": "INTEGER",
                    "description": "Foreign Key (FK) → encounter.id."
                },
                "reference_type": {
                    "type": "VARCHAR",
                    "description": "Type of referenced resource (e.g., appointment, service_request, referral)."
                },
                "reference_id": {
                    "type": "INTEGER",
                    "description": "ID of the referenced resource. Join depends on reference_type."
                },
                "reference_display": {
                    "type": "VARCHAR",
                    "description": "Human-readable display value of referenced resource."
                },
            },
            "join_hint": (
                "encounter.id = based_on.encounter_id, "
                "then conditionally join using reference_type + reference_id"
            ),
            "relationship": (
                "One encounter can be based on multiple resources (1:N polymorphic relationship)"
            ),
            "query_hint": (
                "Use this table when identifying why an encounter was created. "
                "Requires conditional joins."
            )
        },

    }

    # ENCOUNTER_RELATIONSHIPS = [

    #     # Patient join
    #     "encounter JOIN patient ON encounter.subject_id = patient.id",

    #     # Practitioner join (via participant)
    #     "encounter JOIN encounter_participant ON encounter.id = encounter_participant.encounter_id",
    #     "encounter_participant JOIN practitioner ON encounter_participant.individual_reference = practitioner.id",

    #     # Other relations
    #     "encounter JOIN encounter_type ON encounter.id = encounter_type.encounter_id",
    #     "encounter JOIN encounter_diagnosis ON encounter.id = encounter_diagnosis.encounter_id",
    #     "encounter JOIN encounter_location ON encounter.id = encounter_location.encounter_id",
    #     "encounter JOIN encounter_reason_code ON encounter.id = encounter_reason_code.encounter_id",
    #     "encounter JOIN based_on ON encounter.id = based_on.encounter_id",
        
    #     # CONDITIONAL JOIN (IMPORTANT)
    #     "based_on.reference_id maps to external tables depending on reference_type",
    # ]

    ENCOUNTER_RELATIONSHIPS = [

        # SUBJECT (POLYMORPHIC)
        "encounter.subject_id maps to different tables based on encounter.subject_type",
        "If subject_type = 'patient' → encounter.subject_id = patient.id",

        # PRACTITIONER (via participant)
        "encounter LEFT JOIN encounter_participant ON encounter.id = encounter_participant.encounter_id",
        "encounter_participant LEFT JOIN practitioner ON encounter_participant.individual_reference = practitioner.id",

        # ENCOUNTER DETAILS (OPTIONAL → ALWAYS LEFT JOIN)
        "encounter LEFT JOIN encounter_type ON encounter.id = encounter_type.encounter_id",
        "encounter LEFT JOIN encounter_diagnosis ON encounter.id = encounter_diagnosis.encounter_id",
        "encounter LEFT JOIN encounter_location ON encounter.id = encounter_location.encounter_id",
        "encounter LEFT JOIN encounter_reason_code ON encounter.id = encounter_reason_code.encounter_id",

        # BASED ON (POLYMORPHIC)
        "encounter LEFT JOIN based_on ON encounter.id = based_on.encounter_id",

        # CONDITIONAL JOIN LOGIC (VERY IMPORTANT)
        "If based_on.reference_type = 'appointment' → join appointment.id = based_on.reference_id",
        "If based_on.reference_type = 'service_request' → join service_request.id = based_on.reference_id",
    ]

    APPOINTMENT_SCHEMA = {

        "appointment": {
            "description": (
                "Stores scheduled healthcare appointments.\n"
                "Each record represents a booking between a patient and healthcare provider.\n"
                "Used for scheduling, tracking visits, and linking to encounters."
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary Key (PK). Internal identifier used for joins."
                },
                "appointment_id": {
                    "type": "VARCHAR",
                    "description": "External public ID. DO NOT use for joins."
                },
                "user_id": {
                    "type": "INTEGER",
                    "description": "User reference ID."
                },
                "org_id": {
                    "type": "INTEGER",
                    "description": "Organization ID."
                },
                "status": {
                    "type": "VARCHAR",
                    "description": "Appointment status (booked, cancelled, fulfilled, etc)."
                },
                "start": {
                    "type": "TIMESTAMP",
                    "description": "Appointment start datetime."
                },
                "end": {
                    "type": "TIMESTAMP",
                    "description": "Appointment end datetime."
                },
                "minutes_duration": {
                    "type": "INTEGER",
                    "description": "Duration of appointment in minutes."
                },
                "description": {
                    "type": "VARCHAR",
                    "description": "Description of appointment."
                },
                "priority_value": {
                    "type": "INTEGER",
                    "description": "Priority level."
                },
                
                #  SUBJECT (POLYMORPHIC)
                "subject_type": {
                    "type": "VARCHAR",
                    "description": "Type of subject (e.g., patient)."
                },
                "subject_id": {
                    "type": "INTEGER",
                    "description": "ID of subject (join depends on subject_type)."
                },
                "subject_display": {
                    "type": "VARCHAR",
                    "description": "Display name of subject."
                },
                
                # LINK TO ENCOUNTER
                "encounter_id": {
                    "type": "INTEGER",
                    "description": "FK → encounter.id (appointment linked to encounter)."
                },
                "created_at": {
                    "type": "TIMESTAMP",
                    "description": "Record creation timestamp."
                },
                "updated_at": {
                    "type": "TIMESTAMP",
                    "description": "Last updated timestamp."
                },
            },
            "join_hint": "Use appointment.id for joins",
            "role": "Primary table for scheduling and appointment queries",
            "query_hint": "Start from this table for appointment-related queries"
        },

        "appointment_participant": {
            "description": (
                "Stores participants involved in an appointment.\n"
                "Includes patient, practitioner, or other actors."
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key."
                },
                "appointment_id": {
                    "type": "INTEGER",
                    "description": "Foreign Key (FK) → appointment.id"
                },
                "actor_reference_type": {
                    "type": "VARCHAR",
                    "description": "Type of actor (patient, practitioner). Determines join target."
                },
                "actor_reference_id": {
                    "type": "INTEGER",
                    "description": "ID of referenced actor (join depends on actor_reference_type)."
                },
                "actor_display": {
                    "type": "VARCHAR",
                    "description": "Display name of participant."
                },
                "status": {
                    "type": "VARCHAR",
                    "description": "Participation status (accepted, declined, etc)."
                },
            },
            "join_hint": "appointment.id = appointment_participant.appointment_id",
            "relationship": "One appointment can have multiple participants (1:N)",
        },

        "appointment_reason_code": {
            "description": "Stores reason for appointment (symptoms, purpose).",
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key."
                },
                "appointment_id": {
                    "type": "INTEGER",
                    "description": "Foreign Key (FK) → appointment.id"
                },
                "coding_code": {
                    "type": "VARCHAR",
                    "description": "Reason code."
                },
                "coding_display": {
                    "type": "VARCHAR",
                    "description": "Human-readable reason."
                },
                "text": {
                    "type": "VARCHAR",
                    "description": "Additional description."
                },
            },
            "join_hint": "appointment.id = appointment_reason_code.appointment_id",
        },

        "appointment_recurrence_template": {
            "description": (
                "Stores recurrence rules for repeating appointments.\n"
                "Defines frequency such as daily, weekly, monthly."
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key."
                },
                "appointment_id": {
                    "type": "INTEGER",
                    "description": "Foreign Key (FK) → appointment.id"
                },
                "recurrence_type_code": {
                    "type": "VARCHAR",
                    "description": "Frequency (daily, weekly, monthly)."
                },
                "occurrence_count": {
                    "type": "INTEGER",
                    "description": "Number of occurrences."
                },
                "last_occurrence_date": {
                    "type": "DATE",
                    "description": "End date of recurrence."
                },
            },
            "join_hint": "appointment.id = appointment_recurrence_template.appointment_id",
            "relationship": "One appointment has one recurrence template (1:1)",
        },
    }

    APPOINTMENT_RELATIONSHIPS = [

        # SUBJECT (POLYMORPHIC)
        "appointment.subject_id maps to tables based on appointment.subject_type",
        "If subject_type = 'patient' → appointment.subject_id = patient.id",

        # ENCOUNTER LINK
        "appointment LEFT JOIN encounter ON appointment.encounter_id = encounter.id",

        #  PARTICIPANTS
        "appointment LEFT JOIN appointment_participant ON appointment.id = appointment_participant.appointment_id",

        # CONDITIONAL ACTOR JOIN
        "If actor_reference_type = 'patient' → join patient.id",
        "If actor_reference_type = 'practitioner' → join practitioner.id",

        # REASON
        "appointment LEFT JOIN appointment_reason_code ON appointment.id = appointment_reason_code.appointment_id",

        # RECURRENCE
        "appointment LEFT JOIN appointment_recurrence_template ON appointment.id = appointment_recurrence_template.appointment_id",
    ]

    QUESTIONNAIRE_SCHEMA = {

        "questionnaire_response": {
            "description": (
                "Stores responses to structured questionnaires filled by patients or practitioners.\n"
                "Each response belongs to a questionnaire and may be linked to an encounter.\n"
                "Supports nested questions and multiple answer types."
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary Key (PK). Internal identifier used for joins."
                },
                "questionnaire_response_id": {
                    "type": "VARCHAR",
                    "description": "External public ID. DO NOT use for joins."
                },
                "questionnaire": {
                    "type": "VARCHAR",
                    "description": "Canonical URL of the questionnaire."
                },
                "status": {
                    "type": "VARCHAR",
                    "description": "Response status (in-progress, completed, amended)."
                },
                "subject_type": {
                    "type": "VARCHAR",
                    "description": "Type of subject (patient, practitioner)."
                },
                "subject_id": {
                    "type": "INTEGER",
                    "description": "ID of subject (join depends on subject_type)."
                },
                "subject_display": {
                    "type": "VARCHAR",
                    "description": "Display name of subject."
                },
                "authored": {
                    "type": "TIMESTAMP",
                    "description": "Datetime when response was created."
                },
                "author_reference_type": {
                    "type": "VARCHAR",
                    "description": "Type of author (patient/practitioner)."
                },
                "author_reference_id": {
                    "type": "INTEGER",
                    "description": "ID of author."
                },
                "source_reference_type": {
                    "type": "VARCHAR",
                    "description": "Source type (patient/practitioner/device)."
                },
                "source_reference_id": {
                    "type": "INTEGER",
                    "description": "Source ID."
                },
                "created_at": {
                    "type": "TIMESTAMP",
                    "description": "Record creation timestamp."
                },
                "updated_at": {
                    "type": "TIMESTAMP",
                    "description": "Last updated timestamp."
                },

                "created_at": "Record creation timestamp.",
                "updated_at": "Last updated timestamp.",
            },
            "join_hint": "Use questionnaire_response.id for joins",
            "role": "Primary table for questionnaire responses",
            "query_hint": "Start from this table for survey/form-related queries",
        },

        "questionnaire_response_item": {
            "description": (
                "Stores individual questions (items) within a questionnaire response.\n"
                "Supports hierarchical/nested questions using parent_item_id."
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key."
                },
                "response_id": {
                    "type": "VARCHAR",
                    "description": "Foreign Key (FK) → questionnaire_response.id"
                },
                "parent_item_id": {
                    "type": "INTEGER",
                    "description": "Self-reference for nested questions."
                },
                "link_id": {
                    "type": "VARCHAR",
                    "description": "Unique identifier of the question."
                },
                "text": {
                    "type": "VARCHAR",
                    "description": "Question text."
                },
                "definition": {
                    "type": "VARCHAR",
                    "description": "Question definition reference."
                },
            },
            "join_hint": "questionnaire_response.id = questionnaire_response_item.response_id",
            "relationship": "One response has multiple items (1:N, hierarchical)",
        },

        "questionnaire_response_answer": {
            "description": (
                "Stores answers for each questionnaire item.\n"
                "Supports multiple answer types using value_type field.\n\n"
                
                "IMPORTANT:\n"
                "- Only one value column is populated based on value_type\n"
                "- Example:\n"
                "  value_type = 'string' → use value_string\n"
                "  value_type = 'boolean' → use value_boolean\n"
                "  value_type = 'integer' → use value_integer"
            ),
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "description": "Primary key."
                },
                "item_id": {
                    "type": "INTEGER",
                    "description": "Foreign Key (FK) → questionnaire_response_item.id"
                },
                "value_type": {
                    "type": "VARCHAR",
                    "description": "Type of answer (string, boolean, integer, etc)."
                },
                "value_string": {
                    "type": "VARCHAR",
                    "description": "Text answer."
                },
                "value_boolean": {
                    "type": "BOOLEAN",
                    "description": "Boolean answer."
                },
                "value_integer": {
                    "type": "INTEGER",
                    "description": "Integer answer."
                },
                "value_decimal": {
                    "type": "DECIMAL",
                    "description": "Decimal answer."
                },
                "value_datetime": {
                    "type": "DATETIME",
                    "description": "Datetime answer."
                },
                "value_coding_code": {
                    "type": "VARCHAR",
                    "description": "Coded answer value."
                },
                "value_coding_display": {
                    "type": "VARCHAR",
                    "description": "Display text of coded value."
                },
            },
            "join_hint": "questionnaire_response_item.id = questionnaire_response_answer.item_id",
            "relationship": "One item can have multiple answers (1:N)",
            "query_hint": "Use value_type to decide which column to read",
        },
    }

    QUESTIONNAIRE_RELATIONSHIPS = [

        # RESPONSE → ITEM
        "questionnaire_response JOIN questionnaire_response_item ON questionnaire_response.id = questionnaire_response_item.response_id",

        # ITEM → ANSWER
        "questionnaire_response_item JOIN questionnaire_response_answer ON questionnaire_response_item.id = questionnaire_response_answer.item_id",

        # SUBJECT (POLYMORPHIC)
        "questionnaire_response.subject_id maps based on subject_type",
        "If subject_type = 'patient' → join patient.id",

        # ENCOUNTER
        "questionnaire_response LEFT JOIN encounter ON questionnaire_response.encounter_id = encounter.id",

        # AUTHOR (POLYMORPHIC)
        "If author_reference_type = 'patient' → join patient.id",
        "If author_reference_type = 'practitioner' → join practitioner.id",

        # SOURCE (POLYMORPHIC)
        "If source_reference_type = 'patient' → join patient.id",
        "If source_reference_type = 'practitioner' → join practitioner.id",
    ]

    # Example queries for common operations
    EXAMPLE_QUERIES = {

        "get_all_patients": """
            SELECT p.id, p.given_name, p.family_name, p.gender, p.birth_date
            FROM patient p
            ORDER BY p.family_name, p.given_name
            LIMIT 100;
        """,

        "get_patient_by_id": """
            SELECT p.*, pi.system, pi.value AS identifier
            FROM patient p
            LEFT JOIN patient_identifier pi ON p.id = pi.patient_id
            WHERE p.id = :patient_id;
        """,

        "search_patients_by_name": """
            SELECT p.id, p.given_name, p.family_name, p.gender
            FROM patient p
            WHERE p.given_name ILIKE '%' || :name || '%'
            OR p.family_name ILIKE '%' || :name || '%'
            ORDER BY p.family_name, p.given_name
            LIMIT 50;
        """,

        "get_patient_contacts": """
            SELECT p.id, p.given_name, p.family_name,
                pt.system, pt.value, pt.use
            FROM patient p
            LEFT JOIN patient_telecom pt ON p.id = pt.patient_id
            WHERE p.id = :patient_id
            ORDER BY pt.use;
        """,

        "get_patient_addresses": """
            SELECT p.id, p.given_name, p.family_name,
                pa.line, pa.city, pa.state, pa.postal_code, pa.country
            FROM patient p
            LEFT JOIN patient_address pa ON p.id = pa.patient_id
            WHERE p.id = :patient_id
            ORDER BY pa.country, pa.state, pa.city;
        """,
        
        "get_all_practitioners": """
            SELECT p.id, p.given_name, p.family_name, p.role, p.specialty
            FROM practitioner p
            ORDER BY p.family_name, p.given_name
            LIMIT 100;
        """,

        "get_practitioner_contacts": """
            SELECT p.given_name, p.family_name,
                pt.system, pt.value
            FROM practitioner p
            LEFT JOIN practitioner_telecom pt ON p.id = pt.practitioner_id
            WHERE p.id = :practitioner_id;
        """,

        "get_encounters_with_patient": """
            SELECT e.id, e.status, e.class_code,
                p.given_name, p.family_name
            FROM encounter e
            LEFT JOIN patient p 
                ON e.subject_id = p.id
            WHERE e.subject_type = 'patient'
            LIMIT 50;
        """,

        "get_encounter_practitioners": """
            SELECT e.id, pr.given_name, pr.family_name
            FROM encounter e
            LEFT JOIN encounter_participant ep 
                ON e.id = ep.encounter_id
            LEFT JOIN practitioner pr 
                ON ep.individual_reference = pr.id
            WHERE e.id = :encounter_id;
        """,

        "get_doctors_by_specialty": """
            SELECT given_name, family_name, specialty
            FROM practitioner
            WHERE specialty ILIKE '%' || :specialty || '%'
            LIMIT 50;
        """,

        #patients appointment examples 
        "get_appointments_with_patient": """
            SELECT a.id, a.status, a.start,
                p.given_name, p.family_name
            FROM appointment a
            LEFT JOIN patient p 
                ON a.subject_id = p.id
            WHERE a.subject_type = 'patient'
            LIMIT 50;
        """,

        #appointment participant examples
        "get_appointment_participants": """
            SELECT a.id, ap.actor_reference_type,
                ap.actor_reference_id
            FROM appointment a
            LEFT JOIN appointment_participant ap 
                ON a.id = ap.appointment_id
            WHERE a.id = :appointment_id;
        """,

        #appointment encounter examples
        "get_appointments_with_encounter": """
            SELECT a.id, a.status, e.id AS encounter_id
            FROM appointment a
            LEFT JOIN encounter e 
                ON a.encounter_id = e.id
            LIMIT 50;
        """,
        #questionnaire response examples
        "get_questionnaire_responses_with_patient": """
            SELECT qr.id, qr.status,
                p.given_name, p.family_name
            FROM questionnaire_response qr
            LEFT JOIN patient p 
                ON qr.subject_id = p.id
            WHERE qr.subject_type = 'patient'
            LIMIT 50;
        """,
        "get_questionnaire_answers": """
            SELECT qr.id, qri.link_id, qri.text,
                CASE 
                    WHEN qra.value_type = 'string' THEN qra.value_string
                    WHEN qra.value_type = 'boolean' THEN CAST(qra.value_boolean AS TEXT)
                    WHEN qra.value_type = 'integer' THEN CAST(qra.value_integer AS TEXT)
                END AS answer
            FROM questionnaire_response qr
            LEFT JOIN questionnaire_response_item qri 
                ON qr.id = qri.response_id
            LEFT JOIN questionnaire_response_answer qra 
                ON qri.id = qra.item_id
            WHERE qr.id = :response_id;
        """,
        "find_patients_with_answer": """
            SELECT p.given_name, p.family_name, qra.value_string
            FROM questionnaire_response qr
            LEFT JOIN patient p 
                ON qr.subject_id = p.id
            LEFT JOIN questionnaire_response_item qri 
                ON qr.id = qri.response_id
            LEFT JOIN questionnaire_response_answer qra 
                ON qri.id = qra.item_id
            WHERE qra.value_string ILIKE '%' || :keyword || '%'
            AND qr.subject_type = 'patient';
        """,

    }

    # MERGED (FINAL)
    SCHEMA: Dict[str, Dict] = {
        **PATIENT_SCHEMA,
        **PRACTITIONER_SCHEMA,
        **ENCOUNTER_SCHEMA,
        **APPOINTMENT_SCHEMA,
        **QUESTIONNAIRE_SCHEMA,
    }

    RELATIONSHIPS: List[str] = [
        *PATIENT_RELATIONSHIPS,
        *PRACTITIONER_RELATIONSHIPS,
        *ENCOUNTER_RELATIONSHIPS,
        *APPOINTMENT_RELATIONSHIPS,
        *QUESTIONNAIRE_RELATIONSHIPS,
    ]

    @classmethod
    def get_schema(cls):
        return cls.SCHEMA

    @classmethod
    def get_relationships(cls):
        return cls.RELATIONSHIPS

    @classmethod
    def get_example_queries(cls):
        """
        Returns example queries for common operations.
        
        Returns:
            dict: Example SQL queries with descriptions
        """
        return cls.EXAMPLE_QUERIES