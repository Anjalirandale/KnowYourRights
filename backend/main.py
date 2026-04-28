import random

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import crud, models, schemas, security
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KnowYourRights API",
    description="FastAPI backend for authentication and user progress tracking",
    version="1.0.0",
)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:5177",
    "http://localhost:5178",
    "http://localhost:5179",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTION_BANK = [
    {
        "id": 1,
        "domain": "Consumer Rights",
        "difficulty": "easy",
        "scenario": "Rahul purchased a smartphone online for ₹25,000. Within 3 days, the phone stopped working. The seller refuses to replace it, claiming \"electronics are non-returnable once opened\".",
        "question": "What is Rahul's legal right in this situation?",
        "options": {
            "A": "He can demand a replacement or refund within 7 days",
            "B": "He has no rights since electronics are non-returnable",
            "C": "He must accept the loss and buy a new phone",
            "D": "He can only get store credit, not a refund"
        },
        "correct_answer": "A",
        "explanation": "Under the Consumer Protection Act 2019, consumers have the right to seek redressal against unfair trade practices. For defective products, consumers can demand replacement, refund, or compensation within a reasonable timeframe.",
        "legal_reference": "Consumer Protection Act 2019 - Section 2(47)",
        "xp_reward": 10
    },
    {
        "id": 2,
        "domain": "Consumer Rights",
        "difficulty": "medium",
        "scenario": "A restaurant adds a mandatory \"service charge\" of 10% to every bill without informing customers beforehand. When questioned, they claim it's their policy.",
        "question": "Is this practice legally valid?",
        "options": {
            "A": "Yes, restaurants can charge whatever they want",
            "B": "Only if mentioned in the menu",
            "C": "No, service charge must be voluntary and clearly displayed",
            "D": "Yes, but customers can refuse to pay it"
        },
        "correct_answer": "C",
        "explanation": "Service charge is voluntary and cannot be forced upon consumers. The Consumer Affairs Ministry has clarified that customers can refuse to pay service charge if they are not satisfied with the service.",
        "legal_reference": "Consumer Protection Act 2019 - Unfair Trade Practice",
        "xp_reward": 25
    },
    {
        "id": 3,
        "domain": "Labor Law",
        "difficulty": "medium",
        "scenario": "Priya works at a tech company. She was asked to work overtime for 3 hours daily for a month without any additional compensation. When she refused, she was threatened with termination.",
        "question": "What does the law say about overtime compensation?",
        "options": {
            "A": "Employees cannot refuse overtime work",
            "B": "Employers can demand overtime without extra pay",
            "C": "Overtime is only applicable to factory workers",
            "D": "Overtime must be paid at double the normal rate"
        },
        "correct_answer": "D",
        "explanation": "Under labor laws, any work beyond normal working hours must be compensated at overtime rates, typically double the ordinary wage. Employees cannot be forced to work overtime, and refusal is not grounds for termination.",
        "legal_reference": "Factories Act 1948 / Shops and Establishments Act",
        "xp_reward": 25
    },
    {
        "id": 4,
        "domain": "Labor Law",
        "difficulty": "hard",
        "scenario": "A company terminates an employee who has worked for 8 years without providing any reason or notice period. The employee was given only 15 days to leave.",
        "question": "What legal protections does this employee have?",
        "options": {
            "A": "Only entitled to 1 month salary as compensation",
            "B": "Entitled to notice period or pay in lieu, and potential reinstatement",
            "C": "None, companies can fire anyone anytime",
            "D": "Can only file a civil suit which takes years"
        },
        "correct_answer": "B",
        "explanation": "Under the Industrial Disputes Act, employees who have completed 240 days of continuous service cannot be terminated without valid reason and proper procedure. They are entitled to notice period, retrenchment compensation, and can challenge wrongful termination.",
        "legal_reference": "Industrial Disputes Act 1947 - Section 25F",
        "xp_reward": 50
    },
    {
        "id": 5,
        "domain": "Property Law",
        "difficulty": "easy",
        "scenario": "A tenant has been living in a rented apartment for 2 years. The landlord suddenly demands a 50% increase in rent with only 1 week's notice.",
        "question": "Is the landlord's demand legally valid?",
        "options": {
            "A": "Yes, landlords can increase rent anytime",
            "B": "Yes, but maximum 10% increase allowed",
            "C": "Only if the tenant agrees verbally",
            "D": "No, rent increase requires reasonable notice as per agreement"
        },
        "correct_answer": "D",
        "explanation": "Rent increases must follow the terms of the rental agreement. Typically, landlords must provide 1-3 months notice for any rent increase. Arbitrary increases can be challenged under tenancy laws.",
        "legal_reference": "Rent Control Act / State-specific Tenancy Laws",
        "xp_reward": 10
    },
    {
        "id": 6,
        "domain": "Property Law",
        "difficulty": "hard",
        "scenario": "A person buys a property and later discovers that the seller had already mortgaged it to a bank, and the loan is now in default. The bank is claiming the property.",
        "question": "What is the buyer's legal position?",
        "options": {
            "A": "Buyer loses the property as bank has first claim",
            "B": "Buyer must pay off the bank loan to keep the property",
            "C": "Buyer can keep the property if purchase was bona fide and registered",
            "D": "Only option is to sue the seller for fraud"
        },
        "correct_answer": "C",
        "explanation": "If the buyer purchased the property in good faith, completed due diligence, and the sale was properly registered, they may have valid title. However, this depends on whether the mortgage was registered and if the buyer had notice of it. Legal recourse against the seller for fraud is also available.",
        "legal_reference": "Transfer of Property Act 1882 - Section 41",
        "xp_reward": 50
    },
    {
        "id": 7,
        "domain": "Criminal Law",
        "difficulty": "medium",
        "scenario": "A person is arrested by police at 10 PM. The police refuse to inform the family and keep the person in custody overnight without producing them before a magistrate.",
        "question": "What constitutional right is being violated?",
        "options": {
            "A": "Right to be informed of grounds of arrest and right to be produced before magistrate within 24 hours",
            "B": "Only police protocol is violated, not a constitutional right",
            "C": "Right to bail is automatic",
            "D": "Only the right to make a phone call"
        },
        "correct_answer": "A",
        "explanation": "Article 22 of the Constitution guarantees the right to be informed of the grounds of arrest, the right to consult a lawyer, and the right to be produced before a magistrate within 24 hours of arrest.",
        "legal_reference": "Constitution of India - Article 22",
        "xp_reward": 25
    },
    {
        "id": 8,
        "domain": "Criminal Law",
        "difficulty": "easy",
        "scenario": "A woman files a complaint of domestic violence. The police refuse to register an FIR, saying it's a \"family matter\" that should be resolved privately.",
        "question": "What is the legal position?",
        "options": {
            "A": "Police are correct, domestic matters should stay private",
            "B": "The woman must produce witnesses first",
            "C": "Only family court can handle such matters",
            "D": "Police must register FIR; domestic violence is a cognizable offense"
        },
        "correct_answer": "D",
        "explanation": "Domestic violence is a criminal offense under the Protection of Women from Domestic Violence Act. Police are mandated to register complaints and cannot refuse on grounds of it being a \"family matter\".",
        "legal_reference": "Protection of Women from Domestic Violence Act 2005",
        "xp_reward": 10
    },
    {
        "id": 9,
        "domain": "Constitutional Rights",
        "difficulty": "medium",
        "scenario": "A government school denies admission to a child from a marginalized community, citing that the school only admits students from \"respectable families\".",
        "question": "Which fundamental right is being violated?",
        "options": {
            "A": "Cultural and Educational Rights",
            "B": "Right to Equality (Article 14) and Right against Untouchability (Article 17)",
            "C": "Only the Right to Education",
            "D": "Only a moral issue, not a legal violation"
        },
        "correct_answer": "B",
        "explanation": "Article 14 guarantees equality before law, and Article 17 abolishes untouchability. Discrimination based on caste or social status in educational institutions is unconstitutional and illegal.",
        "legal_reference": "Constitution of India - Articles 14, 15, 17",
        "xp_reward": 25
    },
    {
        "id": 10,
        "domain": "Constitutional Rights",
        "difficulty": "hard",
        "scenario": "A state government passes an order prohibiting all public gatherings and protests in the capital city indefinitely, citing maintenance of public order.",
        "question": "Is this order constitutionally valid?",
        "options": {
            "A": "Valid only during emergency declaration",
            "B": "Only political parties can challenge this",
            "C": "Yes, government has absolute power to maintain order",
            "D": "No, it violates the fundamental right to peaceful assembly under reasonable restrictions"
        },
        "correct_answer": "D",
        "explanation": "While the state can impose reasonable restrictions on the right to assembly (Article 19(1)(b)) for public order, a blanket ban on all public gatherings indefinitely is disproportionate and unconstitutional.",
        "legal_reference": "Constitution of India - Article 19(1)(b) and 19(3)",
        "xp_reward": 50
    },
    {
        "id": 11,
        "domain": "Cyber Law",
        "difficulty": "easy",
        "scenario": "Someone discovers that their private photos have been shared on social media without their consent by an ex-partner.",
        "question": "What legal recourse is available?",
        "options": {
            "A": "Nothing can be done once photos are online",
            "B": "Must pay to get them removed",
            "C": "Can file complaint under IT Act for violation of privacy and seek removal",
            "D": "Only option is to contact social media platform"
        },
        "correct_answer": "C",
        "explanation": "Sharing private content without consent is an offense under the IT Act. Victims can file complaints with cyber police, seek removal of content, and pursue criminal charges against the perpetrator.",
        "legal_reference": "Information Technology Act 2000 - Section 66E, 67",
        "xp_reward": 10
    },
    {
        "id": 12,
        "domain": "Cyber Law",
        "difficulty": "medium",
        "scenario": "An e-commerce company stores customer data including credit card information. Their database is hacked, exposing thousands of customers' financial data.",
        "question": "What is the company's legal liability?",
        "options": {
            "A": "Company is liable for failure to implement reasonable security practices",
            "B": "No liability as hacking is a criminal act by third parties",
            "C": "Only liable if customers suffer actual financial loss",
            "D": "Only government can take action, not individuals"
        },
        "correct_answer": "A",
        "explanation": "Under the IT Act and SPDI Rules, companies handling sensitive personal data must implement reasonable security practices. Failure to protect data makes them liable for compensation and penalties.",
        "legal_reference": "IT Act 2000 - Section 43A, SPDI Rules 2011",
        "xp_reward": 25
    },
    {
        "id": 13,
        "domain": "Consumer Rights",
        "difficulty": "hard",
        "scenario": "A pharmaceutical company markets a drug without disclosing known serious side effects. Several patients suffer adverse reactions.",
        "question": "What legal actions can affected patients take?",
        "options": {
            "A": "Nothing, all drugs have side effects",
            "B": "Can only complain to drug controller",
            "C": "Must prove intent to harm for any action",
            "D": "Can sue for product liability, claim compensation, and file criminal complaint"
        },
        "correct_answer": "D",
        "explanation": "Under the Consumer Protection Act 2019, manufacturers are strictly liable for defective products. Patients can claim compensation for product liability, and the company may face criminal action for negligence.",
        "legal_reference": "Consumer Protection Act 2019 - Product Liability (Chapter VI)",
        "xp_reward": 50
    },
    {
        "id": 14,
        "domain": "Labor Law",
        "difficulty": "easy",
        "scenario": "An employee is forced to work 7 days a week without any weekly off for 3 months.",
        "question": "Is this practice legal?",
        "options": {
            "A": "Yes, if mentioned in employment contract",
            "B": "Only illegal if overtime is not paid",
            "C": "No, every employee is entitled to at least one weekly rest day",
            "D": "Legal for private sector employees"
        },
        "correct_answer": "C",
        "explanation": "Labor laws mandate at least one weekly rest day for all employees. Continuous work without weekly rest is illegal and employees can complain to labor authorities.",
        "legal_reference": "Shops and Establishments Act / Factories Act 1948",
        "xp_reward": 10
    },
    {
        "id": 15,
        "domain": "Cyber Law",
        "difficulty": "hard",
        "scenario": "A person creates a fake social media profile impersonating a celebrity and posts defamatory content, causing reputational damage.",
        "question": "What offenses have been committed?",
        "question_type": "mcq",
        "options": {
            "A": "Only civil defamation applies",
            "B": "Identity theft, impersonation, and defamation - all criminal offenses",
            "C": "Celebrity has no legal recourse against anonymous accounts",
            "D": "Only terms of service violation"
        },
        "correct_answer": "B",
        "explanation": "Impersonation and identity theft are offenses under the IT Act. Defamation (criminal and civil) also applies. The victim can file criminal complaints and civil suits for damages.",
        "legal_reference": "IT Act 2000 - Section 66C, 66D, IPC Section 499, 500",
        "xp_reward": 50
    },
    # ── True / False questions ──────────────────────────────────────────
    {
        "id": 16,
        "domain": "Consumer Rights",
        "difficulty": "easy",
        "scenario": "A shop displays a sign saying 'No refunds or exchanges under any circumstances'.",
        "question": "A shop can legally refuse all refunds even for defective products.",
        "question_type": "true_false",
        "correct_answer": "False",
        "explanation": "Under the Consumer Protection Act 2019, consumers have the right to seek redressal for defective goods regardless of any shop policy. A 'no refund' sign does not override statutory consumer rights.",
        "legal_reference": "Consumer Protection Act 2019 - Section 2(9)",
        "xp_reward": 10
    },
    {
        "id": 17,
        "domain": "Labor Law",
        "difficulty": "easy",
        "scenario": "An employer tells a female employee she is not entitled to maternity leave because the company has fewer than 50 employees.",
        "question": "Maternity leave benefits apply only to companies with 50 or more employees.",
        "question_type": "true_false",
        "correct_answer": "False",
        "explanation": "The Maternity Benefit Act 1961 applies to every establishment employing 10 or more persons. The threshold is 10, not 50.",
        "legal_reference": "Maternity Benefit Act 1961 - Section 2",
        "xp_reward": 10
    },
    {
        "id": 18,
        "domain": "Constitutional Rights",
        "difficulty": "medium",
        "scenario": "A citizen is stopped by police for a routine check and asked to show identification documents.",
        "question": "Indian citizens are legally required to carry an identity card at all times.",
        "question_type": "true_false",
        "correct_answer": "False",
        "explanation": "There is no law in India that mandates citizens to carry an identity card at all times. While certain restricted areas may require identification, general movement does not.",
        "legal_reference": "Constitution of India - Article 19(1)(d)",
        "xp_reward": 25
    },
    {
        "id": 19,
        "domain": "Criminal Law",
        "difficulty": "medium",
        "scenario": "A person is arrested and the police officer tells them they can only speak to a lawyer after 48 hours.",
        "question": "An arrested person has the right to consult a lawyer immediately upon arrest.",
        "question_type": "true_false",
        "correct_answer": "True",
        "explanation": "Article 22(1) of the Constitution guarantees every arrested person the right to consult and be defended by a legal practitioner of their choice without any delay.",
        "legal_reference": "Constitution of India - Article 22(1)",
        "xp_reward": 25
    },
    {
        "id": 20,
        "domain": "Cyber Law",
        "difficulty": "hard",
        "scenario": "A company collects biometric data of visitors without informing them, claiming it is for 'security purposes'.",
        "question": "Companies can collect biometric data without explicit consent if it is for security purposes.",
        "question_type": "true_false",
        "correct_answer": "False",
        "explanation": "Collection of biometric data constitutes sensitive personal data under the IT Act's SPDI Rules. Explicit, informed consent is mandatory regardless of the stated purpose.",
        "legal_reference": "IT Act 2000 - SPDI Rules 2011, Rule 5",
        "xp_reward": 50
    },
    # ── Match the Pairs questions ───────────────────────────────────────
    {
        "id": 21,
        "domain": "Constitutional Rights",
        "difficulty": "medium",
        "scenario": "Understanding Fundamental Rights guaranteed by the Indian Constitution.",
        "question": "Match each Fundamental Right with its correct Article number.",
        "question_type": "match_pairs",
        "match_pairs": [
            {"left": "Right to Equality", "right": "Article 14"},
            {"left": "Right to Freedom", "right": "Article 19"},
            {"left": "Right against Exploitation", "right": "Article 23"},
            {"left": "Right to Education", "right": "Article 21A"}
        ],
        "explanation": "The Constitution of India enshrines Fundamental Rights in Part III. Each right is linked to specific articles that define the scope and limitations of that right.",
        "legal_reference": "Constitution of India - Part III",
        "xp_reward": 25
    },
    {
        "id": 22,
        "domain": "Consumer Rights",
        "difficulty": "medium",
        "scenario": "A consumer forum receives complaints involving different types of unfair practices.",
        "question": "Match each consumer right with its correct description.",
        "question_type": "match_pairs",
        "match_pairs": [
            {"left": "Right to Safety", "right": "Protection against hazardous goods"},
            {"left": "Right to Information", "right": "Full disclosure of product details"},
            {"left": "Right to Choose", "right": "Access to variety of goods at fair prices"},
            {"left": "Right to Redressal", "right": "Seek remedy against unfair practices"}
        ],
        "explanation": "The Consumer Protection Act 2019 enshrines six fundamental consumer rights that empower individuals to make informed choices and seek justice.",
        "legal_reference": "Consumer Protection Act 2019 - Section 2(9)",
        "xp_reward": 25
    },
    {
        "id": 23,
        "domain": "Criminal Law",
        "difficulty": "hard",
        "scenario": "A law student is studying different types of offenses and their legal classifications.",
        "question": "Match each type of offense with its correct legal characteristic.",
        "question_type": "match_pairs",
        "match_pairs": [
            {"left": "Cognizable Offense", "right": "Police can arrest without warrant"},
            {"left": "Non-cognizable Offense", "right": "Police need magistrate's order to investigate"},
            {"left": "Bailable Offense", "right": "Accused has right to bail as a matter of right"},
            {"left": "Compoundable Offense", "right": "Can be settled between parties"}
        ],
        "explanation": "The Code of Criminal Procedure classifies offenses into different categories that determine the powers of police and rights of the accused.",
        "legal_reference": "Code of Criminal Procedure 1973 - First Schedule",
        "xp_reward": 50
    },
    {
        "id": 24,
        "domain": "Labor Law",
        "difficulty": "hard",
        "scenario": "An HR manager needs to ensure compliance with various labor welfare provisions.",
        "question": "Match each labor law with its primary purpose.",
        "question_type": "match_pairs",
        "match_pairs": [
            {"left": "Factories Act 1948", "right": "Health, safety and welfare of factory workers"},
            {"left": "Payment of Wages Act 1936", "right": "Timely payment of wages without deductions"},
            {"left": "EPF Act 1952", "right": "Retirement savings and social security"},
            {"left": "ESI Act 1948", "right": "Medical and cash benefits for employees"}
        ],
        "explanation": "India has a comprehensive framework of labor laws, each addressing specific aspects of worker welfare, from wages and safety to social security and healthcare.",
        "legal_reference": "Various Labor Welfare Legislations",
        "xp_reward": 50
    },
    {
        "id": 25,
        "domain": "Cyber Law",
        "difficulty": "medium",
        "scenario": "A cybersecurity analyst is classifying different types of cyber crimes under Indian law.",
        "question": "Match each cyber crime with its corresponding section under the IT Act.",
        "question_type": "match_pairs",
        "match_pairs": [
            {"left": "Hacking / Unauthorized Access", "right": "Section 66"},
            {"left": "Identity Theft", "right": "Section 66C"},
            {"left": "Cyber Stalking", "right": "Section 354D IPC"},
            {"left": "Publishing Obscene Content", "right": "Section 67"}
        ],
        "explanation": "The Information Technology Act 2000 and its amendments define specific sections for different types of cyber offenses, each carrying distinct penalties.",
        "legal_reference": "IT Act 2000 - Sections 66, 66C, 67",
        "xp_reward": 25
    },
]

# Add question_type to legacy MCQ questions that don't have it
for q in QUESTION_BANK:
    if "question_type" not in q:
        q["question_type"] = "mcq"


@app.post("/auth/signup")
def signup(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )
    user = crud.create_user(db, user_create)
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserRead)
def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    return current_user


@app.get("/api/user/progress", response_model=schemas.UserProgressResponse)
def read_user_progress(current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    stats = crud.get_user_stats(db, current_user.id)
    completed = crud.get_completed_scenarios(db, current_user.id)
    xp_history = crud.get_xp_history(db, current_user.id)
    return {
        "user_stats": stats,
        "completed_scenarios": completed,
        "xp_history": xp_history,
    }


@app.put("/api/user/stats", response_model=schemas.UserStatsRead)
def update_user_stats(stats: schemas.UserStatsCreate, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    updated = crud.update_stats(db, current_user.id, stats)
    return updated


@app.post("/api/user/completed-scenarios", response_model=schemas.CompletedScenarioRead)
def add_completed_scenario(scenario: schemas.CompletedScenarioCreate, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    return crud.add_completed_scenario(db, current_user.id, scenario)


@app.post("/api/user/xp-history", response_model=schemas.XPEntryRead)
def add_xp_history(entry: schemas.XPEntryCreate, current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db)):
    return crud.add_xp_entry(db, current_user.id, entry)


@app.get("/questions", response_model=List[schemas.Question])
def list_questions(domain: str = "", difficulty: str = ""):
    filtered = list(QUESTION_BANK)
    if domain:
        filtered = [q for q in filtered if q["domain"].lower() == domain.lower()]
    if difficulty:
        filtered = [q for q in filtered if q["difficulty"].lower() == difficulty.lower()]
    random.shuffle(filtered)
    return filtered
