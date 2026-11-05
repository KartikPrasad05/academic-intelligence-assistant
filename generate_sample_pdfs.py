"""
=============================================================================
COLLEGE DOCUMENT Q&A ASSISTANT - SAMPLE PDF GENERATOR
Generates 100% Valid Standard PDF-1.4 Documents for College Regulations
Zero External Dependencies (Pure Python Implementation)
=============================================================================
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class SimplePDFWriter:
    """Minimal, robust standard PDF-1.4 generator in pure Python."""
    
    def __init__(self, title="College Document"):
        self.title = title
        self.pages = []
        self.current_page_commands = []
        self.current_y = 730
        self.page_width = 612
        self.page_height = 792
        self.margin_left = 50
        self.margin_right = 562
        self.line_height = 14
        
    def _escape_pdf_text(self, text: str) -> str:
        """Escape parentheses and backslashes for PDF string literals."""
        return (
            text.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
            .encode("latin-1", "replace")
            .decode("latin-1")
        )

    def new_page(self):
        """Finalize current page and start a new one."""
        if self.current_page_commands:
            self.pages.append(list(self.current_page_commands))
            self.current_page_commands = []
        self.current_y = 730
        
        # Add running header
        self.current_page_commands.append("BT /F2 9 Tf 0.4 0.4 0.4 rg")
        header_text = self._escape_pdf_text(f"APEX INSTITUTE OF SCIENCE & TECHNOLOGY | {self.title}")
        self.current_page_commands.append(f"50 755 Td ({header_text}) Tj ET")
        # Horizontal rule
        self.current_page_commands.append("0.8 0.8 0.8 RG 1 w 50 748 m 562 748 l S")

    def add_title(self, title: str):
        if not self.pages and not self.current_page_commands:
            self.new_page()
        if self.current_y < 120:
            self.new_page()
            
        esc = self._escape_pdf_text(title)
        self.current_page_commands.append(f"BT /F2 16 Tf 0.05 0.25 0.55 rg 50 {self.current_y} Td ({esc}) Tj ET")
        self.current_y -= 26
        # Decorative underline
        self.current_page_commands.append(f"0.05 0.25 0.55 RG 2 w 50 {self.current_y + 18} m 562 {self.current_y + 18} l S")
        self.current_y -= 10

    def add_heading(self, heading: str):
        if not self.pages and not self.current_page_commands:
            self.new_page()
        if self.current_y < 100:
            self.new_page()
            
        self.current_y -= 10
        esc = self._escape_pdf_text(heading)
        self.current_page_commands.append(f"BT /F2 12 Tf 0.1 0.1 0.1 rg 50 {self.current_y} Td ({esc}) Tj ET")
        self.current_y -= 18

    def add_subheading(self, subheading: str):
        if not self.pages and not self.current_page_commands:
            self.new_page()
        if self.current_y < 80:
            self.new_page()
            
        esc = self._escape_pdf_text(subheading)
        self.current_page_commands.append(f"BT /F2 10 Tf 0.25 0.25 0.25 rg 50 {self.current_y} Td ({esc}) Tj ET")
        self.current_y -= 15

    def add_paragraph(self, text: str):
        if not self.pages and not self.current_page_commands:
            self.new_page()
            
        # Simple word wrap at ~85 characters
        words = text.split()
        lines = []
        current_line = []
        current_len = 0
        
        for w in words:
            if current_len + len(w) + 1 > 82:
                lines.append(" ".join(current_line))
                current_line = [w]
                current_len = len(w)
            else:
                current_line.append(w)
                current_len += len(w) + 1
        if current_line:
            lines.append(" ".join(current_line))
            
        for line in lines:
            if self.current_y < 60:
                self.new_page()
            esc = self._escape_pdf_text(line)
            self.current_page_commands.append(f"BT /F1 10 Tf 0.15 0.15 0.15 rg 50 {self.current_y} Td ({esc}) Tj ET")
            self.current_y -= self.line_height
        self.current_y -= 6

    def add_bullet(self, text: str):
        if not self.pages and not self.current_page_commands:
            self.new_page()
            
        words = text.split()
        lines = []
        current_line = []
        current_len = 0
        
        for w in words:
            if current_len + len(w) + 1 > 78:
                lines.append(" ".join(current_line))
                current_line = [w]
                current_len = len(w)
            else:
                current_line.append(w)
                current_len += len(w) + 1
        if current_line:
            lines.append(" ".join(current_line))
            
        for idx, line in enumerate(lines):
            if self.current_y < 60:
                self.new_page()
            esc = self._escape_pdf_text(line)
            if idx == 0:
                self.current_page_commands.append(f"BT /F2 10 Tf 0.1 0.1 0.1 rg 55 {self.current_y} Td (-) Tj ET")
                self.current_page_commands.append(f"BT /F1 10 Tf 0.15 0.15 0.15 rg 68 {self.current_y} Td ({esc}) Tj ET")
            else:
                self.current_page_commands.append(f"BT /F1 10 Tf 0.15 0.15 0.15 rg 68 {self.current_y} Td ({esc}) Tj ET")
            self.current_y -= self.line_height
        self.current_y -= 4

    def save(self, filepath: Path):
        """Compile and write binary PDF file."""
        if self.current_page_commands:
            self.pages.append(list(self.current_page_commands))
            self.current_page_commands = []
            
        total_pages = len(self.pages)
        objects = []
        
        # Object 1: Catalog
        objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        
        # Object 2: Pages (filled after page objects)
        pages_obj_index = 2
        objects.append(None)  # Placeholder
        
        # Object 3 & 4: Fonts (Helvetica Regular and Bold)
        font_regular_idx = 3
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        font_bold_idx = 4
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        
        page_ref_indices = []
        next_obj_idx = 5
        
        for i, page_cmds in enumerate(self.pages):
            # Add footer with page number
            page_no = i + 1
            footer_text = self._escape_pdf_text(f"Page {page_no} of {total_pages} | Official Academic Publication")
            page_cmds.append("0.8 0.8 0.8 RG 1 w 50 45 m 562 45 l S")
            page_cmds.append(f"BT /F1 8 Tf 0.5 0.5 0.5 rg 220 32 Td ({footer_text}) Tj ET")
            
            stream_content = "\n".join(page_cmds).encode("latin-1")
            stream_len = len(stream_content)
            
            content_obj = f"<< /Length {stream_len} >>\nstream\n".encode("latin-1") + stream_content + b"\nendstream"
            content_obj_idx = next_obj_idx
            objects.append(content_obj)
            next_obj_idx += 1
            
            page_obj = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.page_width} {self.page_height}] "
                f"/Contents {content_obj_idx} 0 R "
                f"/Resources << /Font << /F1 {font_regular_idx} 0 R /F2 {font_bold_idx} 0 R >> >> >>"
            ).encode("latin-1")
            page_obj_idx = next_obj_idx
            objects.append(page_obj)
            page_ref_indices.append(page_obj_idx)
            next_obj_idx += 1
            
        # Now fill Object 2 (Pages)
        kids_str = " ".join([f"{idx} 0 R" for idx in page_ref_indices])
        objects[1] = f"<< /Type /Pages /Kids [{kids_str}] /Count {total_pages} >>".encode("latin-1")
        
        # Construct PDF file with cross-reference table
        output = bytearray()
        output.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        
        xref_offsets = []
        for idx, obj in enumerate(objects):
            xref_offsets.append(len(output))
            obj_num = idx + 1
            output.extend(f"{obj_num} 0 obj\n".encode("latin-1"))
            output.extend(obj)
            output.extend(b"\nendobj\n")
            
        startxref = len(output)
        output.extend(b"xref\n")
        output.extend(f"0 {len(objects) + 1}\n".encode("latin-1"))
        output.extend(b"0000000000 65535 f \n")
        for offset in xref_offsets:
            output.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
            
        output.extend(b"trailer\n")
        output.extend(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("latin-1"))
        output.extend(b"startxref\n")
        output.extend(f"{startxref}\n%%EOF\n".encode("latin-1"))
        
        with open(filepath, "wb") as f:
            f.write(output)
        print(f"[OK] Generated PDF: {filepath.name} ({len(output)} bytes, {total_pages} pages)")


# ---------------------------------------------------------------------------
# Document Data Definitions (Realistic, Comprehensive Academic Documents)
# ---------------------------------------------------------------------------

DOCUMENTS_DATA = {
    "academic_regulations.pdf": {
        "title": "Academic Regulations & Curriculum Guidelines (B.Tech)",
        "sections": [
            {
                "heading": "Section 1: General Academic Structure and Credits",
                "subheading": "1.1 Total Credits Required for Graduation",
                "content": (
                    "Every student admitted to the four-year Bachelor of Technology (B.Tech) degree program "
                    "shall pursue a full-time course of study for eight semesters. The total number of credits "
                    "required for the award of the B.Tech degree is strictly 160 credits. For students admitted "
                    "under the Lateral Entry Scheme into the third semester (second year), the total number of "
                    "credits required for graduation is 120 credits."
                ),
                "bullets": [
                    "Basic Science Courses (BSC): 24 Credits",
                    "Engineering Science Courses (ESC): 22 Credits",
                    "Professional Core Courses (PCC): 60 Credits",
                    "Professional Elective Courses (PEC): 18 Credits",
                    "Open Electives (OEC): 12 Credits",
                    "Humanities, Social Sciences and Management (HSMC): 12 Credits",
                    "Project Work, Seminar and Internship: 12 Credits"
                ]
            },
            {
                "heading": "Section 2: Attendance Requirements and Condonation Rules",
                "subheading": "2.1 Minimum Attendance Requirement",
                "content": (
                    "A student shall be eligible to appear for the semester end examinations only if the student "
                    "acquires a minimum of 75% attendance in aggregate of all subjects registered in that semester. "
                    "Attendance is computed from the date of commencement of instruction up to the last instructional day."
                ),
                "bullets": [
                    "Regular Eligibility: Students securing 75% or greater aggregate attendance are unconditionally eligible for examinations.",
                    "Medical Condonation: Condonation of shortage of attendance between 65% and 74% (inclusive) may be granted on genuine medical grounds.",
                    "Medical Evidence: Medical certificate must be submitted within three working days of resuming classes, duly endorsed by the Head of the Department.",
                    "Condonation Fee: A non-refundable condonation fee of INR 1,000 per semester must be paid before the issuance of examination hall ticket.",
                    "Detention Rule: A candidate who secures aggregate attendance below 65% shall not be permitted to appear for the semester end examinations and shall be declared DETAINED. Such students must repeat the entire semester in the subsequent academic year."
                ]
            },
            {
                "heading": "Section 3: Grading System, CGPA, and Award of Class",
                "subheading": "3.1 10-Point Grading Scale",
                "content": (
                    "The institution follows a continuous assessment model with a 10-point absolute grading scale. "
                    "Marks obtained in Continuous Internal Evaluation (CIE) and Semester End Examination (SEE) are combined."
                ),
                "bullets": [
                    "Grade O (Outstanding): Marks >= 90% | Grade Point: 10.0",
                    "Grade A+ (Excellent): Marks 80% to 89% | Grade Point: 9.0",
                    "Grade A (Very Good): Marks 70% to 79% | Grade Point: 8.0",
                    "Grade B+ (Good): Marks 60% to 69% | Grade Point: 7.0",
                    "Grade B (Above Average): Marks 50% to 59% | Grade Point: 6.0",
                    "Grade C (Pass): Marks 40% to 49% | Grade Point: 5.0",
                    "Grade F (Fail / Backlog): Marks < 40% | Grade Point: 0.0"
                ]
            },
            {
                "heading": "Section 4: Maximum Duration and Promotion Regulations",
                "subheading": "4.1 Time Limit for Degree Completion",
                "content": (
                    "A student must complete all requirements for the B.Tech degree within a maximum span of "
                    "8 academic years (N + 4 years from the date of initial enrollment). A lateral entry student "
                    "must complete the degree within 6 academic years. Failure to meet all academic requirements "
                    "within this window leads to automatic forfeiture of student registration."
                ),
                "bullets": [
                    "Promotion to Year 2: Student must register for all Year 1 courses.",
                    "Promotion to Year 3: Student must successfully clear at least 50% of the total cumulative credits of Year 1 and Year 2 combined.",
                    "Promotion to Year 4: Student must have cleared 100% of Year 1 credits and at least 60% of Year 2 and Year 3 credits."
                ]
            }
        ]
    },

    "examination_guidelines.pdf": {
        "title": "Examination Guidelines, Evaluation Policies and Backlog Rules",
        "sections": [
            {
                "heading": "Section 1: Scheme of Examination and Evaluation",
                "subheading": "1.1 Internal and External Assessment Breakdown",
                "content": (
                    "Each theory course carries a total of 100 marks, partitioned into Continuous Internal Evaluation (CIE) "
                    "accounting for 30 marks, and Semester End Examination (SEE) accounting for 70 marks. "
                    "To qualify for a pass grade in any course, a candidate must obtain a minimum of 35% (25 out of 70 marks) "
                    "in the semester end examination and an aggregate of 40% (40 out of 100 marks) combining CIE and SEE."
                ),
                "bullets": [
                    "Continuous Internal Evaluation (30 Marks): Two Mid-Term examinations (15 marks), Quizzes / Assignments (10 marks), Active attendance and participation (5 marks).",
                    "Semester End Examination (70 Marks): Conducted as a 3-hour centralized written test.",
                    "Part A Question Pattern: 10 compulsory short-answer questions of 2 marks each (20 marks total).",
                    "Part B Question Pattern: 5 essay-type questions of 10 marks each with internal choice (50 marks total)."
                ]
            },
            {
                "heading": "Section 2: Revaluation and Verification Procedure",
                "subheading": "2.1 Step-by-Step Revaluation Guidelines",
                "content": (
                    "A student dissatisfied with their semester end examination marks may apply for photocopy verification "
                    "or revaluation within 15 calendar days from the date of declaration of results on the official portal."
                ),
                "bullets": [
                    "Application Window: Exactly 15 days from official result publication timestamp.",
                    "Revaluation Fee: INR 500 per theory subject (non-refundable unless an upward grade change of 2 grades occurs).",
                    "Evaluation Process: The answer script is coded and independently scrutinized by a senior external evaluator.",
                    "Third Valuation Trigger: If the mark difference between the original examiner and revaluation examiner exceeds 15% of maximum marks, the script is referred to a third evaluator, and the average of the closest two scores is awarded as the final mark.",
                    "No Revaluation: Revaluation is strictly not permissible for Practical/Laboratory exams, Project Viva-Voce, and Internal Assessments."
                ]
            },
            {
                "heading": "Section 3: Supplementary and Backlog Examination Rules",
                "subheading": "3.1 Backlog Registration Protocols",
                "content": (
                    "Supplementary examinations for odd-semester courses are conducted alongside regular odd-semester exams, "
                    "and supplementary examinations for even-semester courses are conducted alongside regular even-semester exams. "
                    "A special fast-track supplementary examination is held exclusively for final-year students (8th semester) "
                    "within 30 days of graduation result announcement."
                ),
                "bullets": [
                    "Maximum Backlog Limit: A candidate can register for a maximum of 6 backlog courses per regular examination cycle.",
                    "Supplementary Examination Fee: INR 350 per course.",
                    "Internal Mark Retention: The CIE marks obtained during regular study are carried forward for all subsequent attempts."
                ]
            },
            {
                "heading": "Section 4: Examination Malpractice and Disciplinary Penalties",
                "subheading": "4.1 Punitive Measures for Unfair Means",
                "content": (
                    "The Examination Malpractice Prevention Committee (EMPC) enforces strict disciplinary actions. "
                    "Unauthorized materials, electronic devices, or communication during exams lead to severe sanctions."
                ),
                "bullets": [
                    "Possession of Notes / Chits / Books: Cancellation of performance in that particular course and forfeiture of the paper.",
                    "Possession of Smart Phones / Smart Watches / Bluetooth devices: Immediate confiscation of device, cancellation of performance in all registered subjects of that examination series, and debarment from 1 subsequent semester examination.",
                    "Impersonation: Criminal case registration with law enforcement, permanent expulsion of both the candidate and the impersonator from the institution."
                ]
            }
        ]
    },

    "student_handbook.pdf": {
        "title": "Student Handbook: Campus Life, Conduct and Policies",
        "sections": [
            {
                "heading": "Section 1: Campus Decorum, Identification and Timings",
                "subheading": "1.1 College Hours and Identity Cards",
                "content": (
                    "The regular instructional hours of the college are from 8:30 AM to 4:45 PM, Monday through Friday. "
                    "Every student must wear the official RFID Student Identity Card prominently around the neck at all times "
                    "while inside the academic campus, laboratories, and library. Security staff are authorized to deny entry "
                    "to any student without a valid ID card."
                ),
                "bullets": [
                    "Campus Gates: In-time cutoff is 8:45 AM. Latecomers require HOD clearance after 3 infractions.",
                    "Central Library Hours: Open from 8:00 AM to 8:00 PM on weekdays; 10:00 AM to 4:00 PM on Saturdays.",
                    "Hostel Timings: Hostel gates close strictly at 9:00 PM for all resident students.",
                    "Vehicle Regulations: Students riding two-wheelers must wear helmets. Speed limit on campus is 20 km/h."
                ]
            },
            {
                "heading": "Section 2: Anti-Ragging Statutory Guidelines",
                "subheading": "2.1 Zero-Tolerance Anti-Ragging Mandate",
                "content": (
                    "Ragging in any form is strictly banned inside and outside the college campus as per UGC Regulations 2009 "
                    "and Supreme Court of India directives. Ragging is defined as any disorderly conduct whether by words spoken "
                    "or written, or by an act which has the effect of teasing, treating or handling with rudeness any student."
                ),
                "bullets": [
                    "Punitive Actions: Immediate suspension, FIR registration with Police, debarment from scholarship, cancellation of admission, and expulsion from hostel.",
                    "National Anti-Ragging Toll-Free Helpline: 1800-180-5522.",
                    "Institutional Anti-Ragging Squad Phone: +91-94401-22334 (Available 24x7).",
                    "Affidavit: Every student and parent must submit an online anti-ragging undertaking at www.antiragging.in."
                ]
            },
            {
                "heading": "Section 3: Library Services, Book Borrowing and E-Resources",
                "subheading": "3.1 Central Library Circulation Guidelines",
                "content": (
                    "The Central Library houses over 85,000 volumes, 120 national and international journals, and digital IEEE/ACM "
                    "subscriptions. Undergraduate students are entitled to borrow 4 books simultaneously for a duration of 14 days."
                ),
                "bullets": [
                    "Overdue Fine: INR 2 per day per book for the first week, and INR 5 per day thereafter.",
                    "Reference Books: Dictionaries, encyclopedias, and single-copy volumes cannot be taken out of the reading room.",
                    "Digital Library: 60 high-speed multimedia workstations with access to NPTEL, IEEE Xplore, and DELNET."
                ]
            }
        ]
    },

    "placement_guidelines.pdf": {
        "title": "Training & Placement Guidelines, Corporate Policies and Eligibility",
        "sections": [
            {
                "heading": "Section 1: Placement Eligibility Criteria",
                "subheading": "1.1 Standard Academic Cutoffs for Campus Recruitment",
                "content": (
                    "Students seeking placement assistance through the Training and Placement Cell (T&P Cell) must satisfy "
                    "the prescribed academic and attendance thresholds. Registration with the T&P portal is mandatory by the 6th semester."
                ),
                "bullets": [
                    "Minimum CGPA: A cumulative grade point average of 6.5 (or 60% aggregate marks) with no standing/active backlogs.",
                    "Secondary School Marks: Minimum 60% in Class 10 (SSC) and Class 12 (Intermediate/CBSE).",
                    "Training Attendance: Minimum 90% attendance in all pre-placement skill development sessions (Aptitude, Coding, Soft Skills).",
                    "Punctuality: Failure to attend a registered campus recruitment test without prior medical leave will lead to debarment from the next 2 visiting companies."
                ]
            },
            {
                "heading": "Section 2: Corporate Recruitment Categorization and Offer Rules",
                "subheading": "2.1 One-Student-One-Offer & Dream Company Policy",
                "content": (
                    "To ensure equitable placement opportunities for all eligible students, the institution operates under a "
                    "structured One-Student-One-Offer policy, categorized by annual compensation tiers."
                ),
                "bullets": [
                    "Tier 3 (Mass Recruiters): Annual package up to INR 4.5 LPA.",
                    "Tier 2 (Core / Product): Annual package between INR 4.5 LPA and INR 9.9 LPA.",
                    "Tier 1 (Dream Companies): Annual package of INR 10.0 LPA and above.",
                    "Upgradation Rule: A student securing an offer in Tier 3 or Tier 2 is eligible to participate exclusively in Tier 1 Dream Company drives until a Dream offer is clinched.",
                    "Acceptance Deadline: An offer letter must be formally accepted or rejected within 48 hours of declaration."
                ]
            },
            {
                "heading": "Section 3: Professional Code of Conduct and Dress Code",
                "subheading": "3.1 Interview Etiquette",
                "content": (
                    "Candidates appearing for corporate interview rounds, group discussions, and presentations must adhere "
                    "to corporate business formal attire. Violation of the dress code will result in immediate disqualification."
                ),
                "bullets": [
                    "Male Attire: Formal crisp shirt, dark trousers, formal blazer/tie, polished dark leather shoes.",
                    "Female Attire: Formal business suit or formal Indian attire (salwar kameez) with formal black shoes/sandals.",
                    "Documentation: 3 updated physical resume copies, original college ID, and portfolio folder."
                ]
            }
        ]
    },

    "department_rules.pdf": {
        "title": "Departmental Regulations, Laboratory Protocols and Capstone Project Rules",
        "sections": [
            {
                "heading": "Section 1: Laboratory Safety and Practical Regulations",
                "subheading": "1.1 Practical Sessions Protocol",
                "content": (
                    "Laboratory courses require systematic record maintenance, active experimentation, and rigorous adherence "
                    "to safety norms. Students must secure at least 75% practical attendance to be qualified for practical exams."
                ),
                "bullets": [
                    "Safety Gear: Cotton lab coats mandatory in chemistry, biology, and workshop labs. Anti-static wristbands in hardware labs.",
                    "Observation Book: Raw experimental data must be checked and initialed by the faculty in-charge on the same day.",
                    "Record Submission: Fair record must be submitted in the subsequent laboratory class. Delay incurs 2 marks deduction per day.",
                    "Breakage / Damage: Inadvertent apparatus damage must be reported to the lab technician. Willful damage incurs a replacement penalty of 1.5x equipment cost."
                ]
            },
            {
                "heading": "Section 2: Final Year Capstone Major Project Guidelines",
                "subheading": "2.1 Project Formation, Review Schedule and Thesis Submission",
                "content": (
                    "The Final Year B.Tech Capstone Project is a 10-credit course spanning the 7th and 8th semesters. "
                    "It demands comprehensive literature review, problem formulation, system design, testing, and documentation."
                ),
                "bullets": [
                    "Team Size: Exactly 3 to 4 students per batch. Inter-departmental teams require prior permission from both Department Heads.",
                    "Guide Allocation: Guides are assigned based on student specialization and faculty research domain in Week 2 of Semester 7.",
                    "Progress Reviews: Three mandatory internal reviews (Phase 1: Problem Definition 20%, Phase 2: Design & Mid-term Implementation 30%, Phase 3: Final Testing & Demonstration 50%).",
                    "Plagiarism Ceiling: The final project dissertation must have a plagiarism similarity index strictly below 15% (excluding references) checked using Turnitin/iThenticate.",
                    "Publication Incentive: Teams publishing a paper in an IEEE/Scopus indexed conference receive 5 bonus evaluation points."
                ]
            }
        ]
    }
}


def generate_all_sample_documents():
    """Generates both valid PDF documents and text companions in data/."""
    print("==========================================================")
    print("Generating Pristine College Academic Documents in data/...")
    print("==========================================================")
    
    for filename, doc_data in DOCUMENTS_DATA.items():
        pdf_path = DATA_DIR / filename
        txt_path = DATA_DIR / (Path(filename).stem + ".txt")
        
        # 1. Build PDF using SimplePDFWriter
        writer = SimplePDFWriter(title=doc_data["title"])
        writer.add_title(doc_data["title"])
        
        txt_lines = [f"{doc_data['title'].upper()}", "=" * len(doc_data['title']), ""]
        
        for section in doc_data["sections"]:
            writer.add_heading(section["heading"])
            writer.add_subheading(section["subheading"])
            writer.add_paragraph(section["content"])
            
            txt_lines.append(f"\n{section['heading']}")
            txt_lines.append(f"{section['subheading']}")
            txt_lines.append(section["content"])
            txt_lines.append("\nKey Provisions:")
            
            for bullet in section.get("bullets", []):
                writer.add_bullet(bullet)
                txt_lines.append(f"  * {bullet}")
            txt_lines.append("")
            
        writer.save(pdf_path)
        
        # 2. Also write high-fidelity plain text companion for instant fallback extraction
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(txt_lines))
        print(f"[OK] Generated Text Companion: {txt_path.name}")
        
    print("\n[SUCCESS] All 5 College Documents Generated Successfully in:")
    print(f"          {DATA_DIR}\n")


if __name__ == "__main__":
    generate_all_sample_documents()
