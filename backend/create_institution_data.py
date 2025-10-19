#!/usr/bin/env python3
"""
Script to create comprehensive institution data in the database
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text
import json

# Institution data
institution_data = {
    "institution": {
        "name": "Malla Reddy College of Engineering & Technology",
        "affiliation": "Permanently Affiliated to JNTUH",
        "approvals": [
            "Approved by AICTE",
            "Accredited by NBA & NAAC-A-Grade",
            "ISO 9001:2008 Certified"
        ],
        "address": "Maisammaguda, Dhulapally Post, Via Hakimpet, Secunderabad–500100"
    },
    "department": "Department of Computational Intelligence",
    "academic_year": "2025-26",
    "effective_date": "2025-06-02",
    "sections": [
        {
            "section": "A",
            "room_number": "4208",
            "class_incharge": "Dr. Kanniaah",
            "timetable": {
                "days": [
                    {
                        "day": "Monday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject": "CN", "subject_full": "Computer Networks"},
                            {"slot": 2, "time": "10:30-11:40", "subject": "R&A", "subject_full": "Robotics and Automation"},
                            {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                            {"slot": 3, "time": "11:50-13:00", "subject": "ML", "subject_full": "Machine Learning"},
                            {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                            {"slot": 4, "time": "13:50-14:50", "subject": "ML LAB", "subject_full": "Machine Learning Lab"},
                            {"slot": 5, "time": "14:50-15:50", "subject": None, "subject_full": None}
                        ]
                    },
                    {
                        "day": "Tuesday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                            {"slot": 2, "time": "10:30-11:40", "subject": "CN", "subject_full": "Computer Networks"},
                            {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                            {"slot": 3, "time": "11:50-13:00", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                            {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                            {"slot": 4, "time": "13:50-14:50", "subject": "PSD", "subject_full": "Professional Skill Development"},
                            {"slot": 5, "time": "14:50-15:50", "subject": "ML", "subject_full": "Machine Learning"}
                        ]
                    },
                    {
                        "day": "Wednesday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject": "ML", "subject_full": "Machine Learning"},
                            {"slot": 2, "time": "10:30-11:40", "subject": "R&A", "subject_full": "Robotics and Automation"},
                            {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                            {"slot": 3, "time": "11:50-13:00", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                            {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                            {"slot": 4, "time": "13:50-14:50", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                            {"slot": 5, "time": "14:50-15:50", "subject": "NEOPAT", "subject_full": None}
                        ]
                    },
                    {
                        "day": "Thursday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject": "CN", "subject_full": "Computer Networks"},
                            {"slot": 2, "time": "10:30-11:40", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                            {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                            {"slot": 3, "time": "11:50-13:00", "subject": "R&A", "subject_full": "Robotics and Automation"},
                            {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                            {"slot": 4, "time": "13:50-14:50", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                            {"slot": 5, "time": "14:50-15:50", "subject": "CN", "subject_full": "Computer Networks"}
                        ]
                    },
                    {
                        "day": "Friday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                            {"slot": 2, "time": "10:30-11:40", "subject": "R&A", "subject_full": "Robotics and Automation"},
                            {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                            {"slot": 3, "time": "11:50-13:00", "subject": "NEOPAT", "subject_full": None},
                            {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                            {"slot": 4, "time": "13:50-14:50", "subject": "CN LAB", "subject_full": "Computer Networks Lab"},
                            {"slot": 5, "time": "14:50-15:50", "subject": None, "subject_full": None}
                        ]
                    },
                    {
                        "day": "Saturday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                            {"slot": 2, "time": "10:30-11:40", "subject": "AD-1", "subject_full": "Application Development – 1"},
                            {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                            {"slot": 3, "time": "11:50-13:00", "subject": "AD-1", "subject_full": "Application Development – 1"},
                            {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                            {"slot": 4, "time": "13:50-14:50", "subject": "ML", "subject_full": "Machine Learning"},
                            {"slot": 5, "time": "14:50-15:50", "subject": "PSD", "subject_full": "Professional Skill Development"}
                        ]
                    }
                ]
            },
            "subjects": [
                {"code": "R22A6602", "name": "Machine Learning", "faculty": "Dr. Kanniaah"},
                {"code": "R22A6617", "name": "Design and Analysis of Computer Algorithms", "faculty": "Dr. Padmalatha"},
                {"code": "R22A0512", "name": "Computer Networks", "faculty": "Mr. D. Santhosh Kumar"},
                {"code": "R22A6702", "name": "Introduction to Data Science", "faculty": "Mr. N. Sateesh"},
                {"code": "R22A6681", "name": "Machine Learning Lab", "faculty": "Dr. Kanniaah / Mr. Sateesh"},
                {"code": "R22A0596", "name": "Computer Networks Lab", "faculty": "Radhika / N. Mahesh Babu"},
                {"code": "R22A6692", "name": "Application Development – 1", "faculty": "Dr. Kanniaah / Vamsi"},
                {"code": "R22A0351", "name": "Robotics and Automation", "faculty": "Dr. Arun Kumar"},
                {"code": "R22A0084", "name": "Professional Skill Development", "faculty": "Dr. Paromitha"}
            ]
        },
        {
            "section": "B",
            "room_number": "4210",
            "class_incharge": "Mrs. Jayasri",
            "timetable": {
                "days": [
                    {
                        "day": "Monday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                            {"slot": 2, "time": "10:30-11:40", "subject": "PSD", "subject_full": "Professional Skill Development"},
                            {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                            {"slot": 3, "time": "11:50-13:00", "subject": "ML", "subject_full": "Machine Learning"},
                            {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                            {"slot": 4, "time": "13:50-14:50", "subject": "NEOPAT", "subject_full": None},
                            {"slot": 5, "time": "14:50-15:50", "subject": "R&A", "subject_full": "Robotics and Automation"}
                        ]
                    },
                    {
                        "day": "Tuesday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject": "R&A", "subject_full": "Robotics and Automation"},
                            {"slot": 2, "time": "10:30-11:40", "subject": "ML LAB", "subject_full": "Machine Learning Lab"},
                            {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                            {"slot": 3, "time": "11:50-13:00", "subject": "ML LAB", "subject_full": "Machine Learning Lab"},
                            {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                            {"slot": 4, "time": "13:50-14:50", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                            {"slot": 5, "time": "14:50-15:50", "subject": "CN", "subject_full": "Computer Networks"}
                        ]
                    },
                    {
                        "day": "Wednesday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject": "ML", "subject_full": "Machine Learning"},
                            {"slot": 2, "time": "10:30-11:40", "subject": "CN LAB", "subject_full": "Computer Networks Lab"},
                            {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                            {"slot": 3, "time": "11:50-13:00", "subject": "CN LAB", "subject_full": "Computer Networks Lab"},
                            {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                            {"slot": 4, "time": "13:50-14:50", "subject": "ML", "subject_full": "Machine Learning"},
                            {"slot": 5, "time": "14:50-15:50", "subject": "IDS", "subject_full": "Introduction to Data Science"}
                        ]
                    },
                    {
                        "day": "Thursday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                            {"slot": 2, "time": "10:30-11:40", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                            {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                            {"slot": 3, "time": "11:50-13:00", "subject": "CN", "subject_full": "Computer Networks"},
                            {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                            {"slot": 4, "time": "13:50-14:50", "subject": "NEOPAT", "subject_full": None},
                            {"slot": 5, "time": "14:50-15:50", "subject": "PSD", "subject_full": "Professional Skill Development"}
                        ]
                    },
                    {
                        "day": "Friday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject": "CN", "subject_full": "Computer Networks"},
                            {"slot": 2, "time": "10:30-11:40", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                            {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                            {"slot": 3, "time": "11:50-13:00", "subject": "R&A", "subject_full": "Robotics and Automation"},
                            {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                            {"slot": 4, "time": "13:50-14:50", "subject": "AD-1", "subject_full": "Application Development – 1"},
                            {"slot": 5, "time": "14:50-15:50", "subject": None, "subject_full": None}
                        ]
                    },
                    {
                        "day": "Saturday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject": "DAA", "subject_full": "Design and Analysis of Computer Algorithms"},
                            {"slot": 2, "time": "10:30-11:40", "subject": "CN", "subject_full": "Computer Networks"},
                            {"slot": "Break", "time": "11:40-11:50", "subject": "Bio Break", "subject_full": None},
                            {"slot": 3, "time": "11:50-13:00", "subject": "IDS", "subject_full": "Introduction to Data Science"},
                            {"slot": "Lunch", "time": "13:00-13:50", "subject": "Lunch Break", "subject_full": None},
                            {"slot": 4, "time": "13:50-14:50", "subject": "ML", "subject_full": "Machine Learning"},
                            {"slot": 5, "time": "14:50-15:50", "subject": "R&A", "subject_full": "Robotics and Automation"}
                        ]
                    }
                ]
            },
            "subjects": [
                {"code": "R22A6602", "name": "Machine Learning", "faculty": "Dr. Rakesh"},
                {"code": "R22A6617", "name": "Design and Analysis of Computer Algorithms", "faculty": "Mrs. Jayasri"},
                {"code": "R22A0512", "name": "Computer Networks", "faculty": "Mr. D. Santhosh Kumar"},
                {"code": "R22A6702", "name": "Introduction to Data Science", "faculty": "Mr. Chandra Sekhar"},
                {"code": "R22A6681", "name": "Machine Learning Lab", "faculty": "Dr. Rakesh / Mrs. S.K. Subhani"},
                {"code": "R22A0596", "name": "Computer Networks Lab", "faculty": "Dr. Gayatri / Dr. Venkata Ramudu"},
                {"code": "R22A6692", "name": "Application Development – 1", "faculty": "Dr. Saiprasad / Dr. Venkata Ramudu"},
                {"code": "R22A0351", "name": "Robotics and Automation", "faculty": "Dr. Arun Kumar"},
                {"code": "R22A0084", "name": "Professional Skill Development", "faculty": "Mr. B. Anjaneyulu"}
            ]
        },
        {
            "section": "C",
            "room_number": "4211",
            "class_incharge": "Mr. N. Mahesh Babu",
            "timetable": {
                "days": [
                    {
                        "day": "Monday",
                        "slots": [
                            {"slot": 1, "time": "9:20-10:30", "subject