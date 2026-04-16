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
                "id": (
                    "Primary Key (PK). Internal identifier used for joins."
                ),
                "patient_id": (
                    "External identifier. DO NOT use for joins. "
                    "Always use 'id' for joins."
                ),
                "given_name": "First name of the patient.",
                "family_name": "Last name of the patient.",
                "gender": "Gender of the patient (male, female, other).",
                "birth_date": "Date of birth of the patient.",
                "active": "Indicates if patient is active.",
                "deceased_boolean": "Indicates if patient is deceased."
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
                "id": "Primary key for the identifier record.",
                "patient_id": (
                    "Foreign key referencing patient.id. Used to link identifiers to a patient."
                ),
                "system": (
                    "Type of identifier (e.g., 'Aadhar', 'Passport', 'Insurance')."
                ),
                "value": (
                    "Actual identifier value assigned to the patient."
                ),
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
                "id": "Primary Key (PK). Unique telecom record.",
                "patient_id": "Foreign Key (FK) → patient.id. Used for joins.",
                "system": "Contact type: phone, email, sms.",
                "value": "Actual contact value.",
                "use": "Usage type: home, work, mobile."
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
                "id": "Primary Key (PK). Unique address record.",
                "patient_id": "Foreign Key (FK) → patient.id. Used for joins.",
                "line": "Street address or house details.",
                "city": "City where the patient resides.",
                "state": "State or region of the patient.",
                "postal_code": "ZIP or postal code.",
                "country": "Country of residence."
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
                "id": "Primary Key (PK). Internal identifier used for joins.",
                "practitioner_id": "External public ID. DO NOT use for joins.",
                "user_id": "User reference ID.",
                "org_id": "Organization ID.",
                "active": "Indicates if practitioner is active.",
                "given_name": "First name of practitioner.",
                "family_name": "Last name of practitioner.",
                "gender": "Gender of practitioner.",
                "birth_date": "Date of birth.",
                "role": "Role (doctor, nurse, specialist).",
                "specialty": "Medical specialty.",
                "deceased_boolean": "Whether practitioner is deceased.",
                "deceased_datetime": "Date/time of death.",
                "created_at": "Record creation timestamp.",
                "updated_at": "Last updated timestamp.",
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
                    "id": "Primary key.",
                    "practitioner_id": "Foreign Key (FK) → practitioner.id",
                    "org_id": "Organization ID.",
                    "system": "Type of identifier (license, registration).",
                    "value": "Identifier value.",
                    "use": "Usage type.",
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
                "id": "Primary key.",
                "practitioner_id": "Foreign Key (FK) → practitioner.id",
                "org_id": "Organization ID.",
                "use": "Address usage type.",
                "type": "Address type.",
                "text": "Full address text.",
                "line": "Street address.",
                "city": "City.",
                "district": "District.",
                "state": "State.",
                "postal_code": "ZIP or postal code.",
                "country": "Country.",
            },
            "join_hint": "practitioner.id = practitioner_address.practitioner_id",
            "relationship": "One practitioner can have multiple addresses (1:N)",
        },

        "practitioner_qualification": {
            "description": (
                "Stores practitioner qualifications such as degrees, certifications, and issuing organizations."
            ),
            "columns": {
                "id": "Primary key.",
                "practitioner_id": "Foreign Key (FK) → practitioner.id",
                "org_id": "Organization ID.",
                "identifier_system": "Qualification identifier system.",
                "identifier_value": "Qualification identifier value.",
                "code_text": "Qualification (MD, PhD, etc).",
                "issuer": "Organization issuing the qualification.",
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
                "id": "Primary Key (PK). Internal ID used for joins.",
                "encounter_id": "External public ID. DO NOT use for joins.",
                "user_id": "User reference ID.",
                "org_id": "Organization ID.",
                "status": "Encounter status (planned, in-progress, finished, cancelled).",
                "class_code": "Type of encounter (inpatient, outpatient, emergency).",
                "priority": "Priority level.",
                "subject_type": "Type of subject (patient).",
                "subject_id": "Reference ID → patient.id",
                "subject_display": "Display name of subject.",
                "period_start": "Start time of encounter.",
                "period_end": "End time of encounter.",
                "created_at": "Creation timestamp.",
                "updated_at": "Last updated timestamp.",
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
                "id": "Primary key.",
                "encounter_id": "FK → encounter.id",
                "org_id": "Organization ID.",
                "type_text": "Role (Primary Physician, Consultant).",
                "reference_type": "Type of participant (practitioner).",
                "individual_reference": "Reference ID → practitioner.id",
                "period_start": "Participation start time.",
                "period_end": "Participation end time.",
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
                "id": "Primary key",
                "encounter_id": "FK → encounter.id",
                "condition_reference": "Reference to condition",
                "use_text": "Usage (admission, discharge)",
                "rank": "Priority rank",
            },
            "join_hint": "encounter.id = encounter_diagnosis.encounter_id",
        },

        "encounter_location": {
            "description": "Stores location details for encounter",
            "columns": {
                "id": "Primary key",
                "encounter_id": "FK → encounter.id",
                "location_reference": "Location reference",
                "status": "Location status",
                "period_start": "Start time",
                "period_end": "End time",
            },
            "join_hint": "encounter.id = encounter_location.encounter_id",
        },

        "encounter_reason_code": {
            "description": "Stores reasons for encounter",
            "columns": {
                "id": "Primary key",
                "encounter_id": "FK → encounter.id",
                "coding_system": "Code system",
                "coding_code": "Code",
                "coding_display": "Display",
                "text": "Reason description",
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
                "id": "Primary key.",
                "encounter_id": "Foreign Key (FK) → encounter.id.",
                "reference_type": (
                    "Type of referenced resource (e.g., appointment, service_request, referral)."
                ),
                "reference_id": (
                    "ID of the referenced resource. Join depends on reference_type."
                ),
                "reference_display": (
                    "Human-readable display value of the referenced resource."
                ),
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
                "id": "Primary Key (PK). Internal identifier used for joins.",
                "appointment_id": "External public ID. DO NOT use for joins.",
                "user_id": "User reference ID.",
                "org_id": "Organization ID.",
                "status": "Appointment status (booked, cancelled, fulfilled, etc).",
                "start": "Appointment start datetime.",
                "end": "Appointment end datetime.",
                "minutes_duration": "Duration of appointment in minutes.",
                "description": "Description of appointment.",
                "priority_value": "Priority level.",
                
                #  SUBJECT (POLYMORPHIC)
                "subject_type": "Type of subject (e.g., patient).",
                "subject_id": "ID of subject (join depends on subject_type).",

                # LINK TO ENCOUNTER
                "encounter_id": "FK → encounter.id (appointment linked to encounter).",

                "created_at": "Record creation timestamp.",
                "updated_at": "Last updated timestamp.",
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
                "id": "Primary key.",
                "appointment_id": "Foreign Key (FK) → appointment.id",
                "actor_reference_type": (
                    "Type of actor (patient, practitioner). Determines join target."
                ),
                "actor_reference_id": (
                    "ID of referenced actor (join depends on actor_reference_type)."
                ),
                "actor_display": "Display name of participant.",
                "status": "Participation status (accepted, declined, etc).",
            },
            "join_hint": "appointment.id = appointment_participant.appointment_id",
            "relationship": "One appointment can have multiple participants (1:N)",
        },

        "appointment_reason_code": {
            "description": "Stores reason for appointment (symptoms, purpose).",
            "columns": {
                "id": "Primary key.",
                "appointment_id": "Foreign Key (FK) → appointment.id",
                "coding_code": "Reason code.",
                "coding_display": "Human-readable reason.",
                "text": "Additional description.",
            },
            "join_hint": "appointment.id = appointment_reason_code.appointment_id",
        },

        "appointment_recurrence_template": {
            "description": (
                "Stores recurrence rules for repeating appointments.\n"
                "Defines frequency such as daily, weekly, monthly."
            ),
            "columns": {
                "id": "Primary key.",
                "appointment_id": "Foreign Key (FK) → appointment.id",
                "recurrence_type_code": "Frequency (daily, weekly, monthly).",
                "occurrence_count": "Number of occurrences.",
                "last_occurrence_date": "End date of recurrence.",
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
                "id": "Primary Key (PK). Internal identifier used for joins.",
                "questionnaire_response_id": "External public ID. DO NOT use for joins.",
                "questionnaire": "Canonical URL of the questionnaire.",
                "status": "Response status (in-progress, completed, amended).",

                # SUBJECT (POLYMORPHIC)
                "subject_type": "Type of subject (patient, practitioner).",
                "subject_id": "ID of subject (join depends on subject_type).",

                # ENCOUNTER LINK
                "encounter_id": "FK → encounter.id",

                "authored": "Datetime when response was created.",

                # AUTHOR (POLYMORPHIC)
                "author_reference_type": "Type of author (patient/practitioner).",
                "author_reference_id": "ID of author.",

                # SOURCE (POLYMORPHIC)
                "source_reference_type": "Source type (patient/practitioner/device).",
                "source_reference_id": "Source ID.",

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
                "id": "Primary key.",
                "response_id": "Foreign Key (FK) → questionnaire_response.id",
                "parent_item_id": "Self-reference for nested questions.",
                "link_id": "Unique identifier of the question.",
                "text": "Question text.",
                "definition": "Question definition reference.",
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
                "id": "Primary key.",
                "item_id": "Foreign Key (FK) → questionnaire_response_item.id",
                "value_type": "Type of answer (string, boolean, integer, etc).",

                "value_string": "Text answer.",
                "value_boolean": "Boolean answer.",
                "value_integer": "Integer answer.",
                "value_decimal": "Decimal answer.",
                "value_datetime": "Datetime answer.",

                "value_coding_code": "Coded answer value.",
                "value_coding_display": "Display text of coded value.",
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