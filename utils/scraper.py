"""
WAEC Past Questions Scraper
Run once: python utils/scraper.py
"""
import requests
from bs4 import BeautifulSoup
import json
import os
import time

SUBJECTS = {
    "mathematics": "https://www.examguru.com.ng/waec-past-questions/mathematics/",
    "physics": "https://www.examguru.com.ng/waec-past-questions/physics/",
    "chemistry": "https://www.examguru.com.ng/waec-past-questions/chemistry/",
    "biology": "https://www.examguru.com.ng/waec-past-questions/biology/",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

FALLBACK_CONTENT = {
    "mathematics": [
        {"question": "If 2x + 3 = 11, find x.", "answer": "x = 4", "topic": "Linear Equations", "year": "2023"},
        {"question": "Find the simple interest on N5,000 at 8% per annum for 3 years.", "answer": "SI = PRT/100 = 5000x8x3/100 = N1,200", "topic": "Simple Interest", "year": "2022"},
        {"question": "A triangle has angles in ratio 2:3:4. Find the largest angle.", "answer": "Largest angle = 4/9 x 180 = 80 degrees", "topic": "Angles", "year": "2022"},
        {"question": "Factorise completely: x^2 - 5x + 6", "answer": "(x-2)(x-3)", "topic": "Factorisation", "year": "2021"},
        {"question": "If log(2) = 0.3010, find log(8)", "answer": "log(8) = 3 x log(2) = 0.9030", "topic": "Logarithms", "year": "2021"},
        {"question": "A car travels 120km in 2 hours. What is its average speed?", "answer": "Speed = 120/2 = 60 km/h", "topic": "Speed and Distance", "year": "2020"},
        {"question": "Find the area of a circle with radius 7cm.", "answer": "Area = 22/7 x 7^2 = 154 cm^2", "topic": "Mensuration", "year": "2020"},
        {"question": "Solve: x + y = 7, x - y = 3", "answer": "x = 5, y = 2", "topic": "Simultaneous Equations", "year": "2019"},
        {"question": "The mean of 5 numbers is 12. Four are 10, 14, 8, 16. Find the fifth.", "answer": "Fifth = 60 - 48 = 12", "topic": "Statistics", "year": "2019"},
        {"question": "If P = {2,3,5,7} and Q = {1,3,5,9}, find P intersection Q", "answer": "{3,5}", "topic": "Sets", "year": "2018"},
        {"question": "A man sells a shirt for N2,400 making 20% profit. Find cost price.", "answer": "CP = 2400/1.2 = N2,000", "topic": "Profit and Loss", "year": "2018"},
        {"question": "Expand (2x + 3)^2", "answer": "4x^2 + 12x + 9", "topic": "Algebraic Expansion", "year": "2017"},
        {"question": "A rectangle is 15m long and 8m wide. Find its perimeter.", "answer": "P = 2(15+8) = 46m", "topic": "Perimeter", "year": "2017"},
        {"question": "Convert 45 degrees to radians.", "answer": "pi/4 radians", "topic": "Trigonometry", "year": "2016"},
        {"question": "Find the gradient of 3y = 6x + 9", "answer": "gradient = 2", "topic": "Coordinate Geometry", "year": "2016"},
    ],
    "physics": [
        {"question": "State Newton's Second Law of Motion.", "answer": "F = ma. The rate of change of momentum is proportional to applied force.", "topic": "Newton's Laws", "year": "2023"},
        {"question": "A body of mass 5kg is acted on by 20N. Find acceleration.", "answer": "a = F/m = 20/5 = 4 m/s^2", "topic": "Newton's Laws", "year": "2023"},
        {"question": "What is the unit of electric potential?", "answer": "Volt (V)", "topic": "Electricity", "year": "2022"},
        {"question": "A wave has frequency 500Hz and wavelength 0.6m. Find speed.", "answer": "v = fl = 500 x 0.6 = 300 m/s", "topic": "Waves", "year": "2022"},
        {"question": "Define specific heat capacity.", "answer": "Heat needed to raise 1kg of a substance by 1 degree Celsius", "topic": "Thermal Physics", "year": "2021"},
        {"question": "Object dropped from 20m. Find time to reach ground. g=10m/s^2", "answer": "t = sqrt(2h/g) = sqrt(4) = 2 seconds", "topic": "Mechanics", "year": "2021"},
        {"question": "What type of lens is used in a camera?", "answer": "Convex (converging) lens", "topic": "Optics", "year": "2020"},
        {"question": "Calculate resistance if V=12V and I=3A.", "answer": "R = V/I = 12/3 = 4 Ohms", "topic": "Electricity", "year": "2020"},
        {"question": "What is the principle behind a transformer?", "answer": "Electromagnetic induction", "topic": "Electromagnetism", "year": "2019"},
        {"question": "State the law of conservation of energy.", "answer": "Energy cannot be created or destroyed, only converted.", "topic": "Energy", "year": "2019"},
        {"question": "Mass 10kg at height 5m. Find potential energy. g=10m/s^2", "answer": "PE = mgh = 10 x 10 x 5 = 500 J", "topic": "Energy", "year": "2018"},
        {"question": "What happens to gas pressure when volume decreases at constant temperature?", "answer": "Pressure increases (Boyle's Law)", "topic": "Gas Laws", "year": "2018"},
        {"question": "Define refraction of light.", "answer": "Bending of light as it passes between media of different optical density", "topic": "Optics", "year": "2017"},
        {"question": "Calculate power of machine doing 600J in 30 seconds.", "answer": "P = W/t = 600/30 = 20 W", "topic": "Work and Power", "year": "2017"},
        {"question": "Difference between speed and velocity?", "answer": "Speed is scalar, velocity is vector (has direction)", "topic": "Mechanics", "year": "2016"},
    ],
    "chemistry": [
        {"question": "What is the chemical formula of table salt?", "answer": "NaCl", "topic": "Chemical Formulas", "year": "2023"},
        {"question": "Balance: H2 + O2 -> H2O", "answer": "2H2 + O2 -> 2H2O", "topic": "Chemical Equations", "year": "2023"},
        {"question": "State the Periodic Law.", "answer": "Properties of elements are periodic functions of atomic number.", "topic": "Periodic Table", "year": "2022"},
        {"question": "What is the pH of a neutral solution?", "answer": "pH = 7", "topic": "Acids and Bases", "year": "2022"},
        {"question": "Define electrolysis.", "answer": "Decomposition of a substance by passing electric current through it", "topic": "Electrolysis", "year": "2021"},
        {"question": "How many moles in 44g of CO2? (C=12, O=16)", "answer": "1 mole", "topic": "Mole Concept", "year": "2021"},
        {"question": "What type of bond exists in NaCl?", "answer": "Ionic bond", "topic": "Chemical Bonding", "year": "2020"},
        {"question": "State Avogadro's number.", "answer": "6.02 x 10^23", "topic": "Mole Concept", "year": "2020"},
        {"question": "Difference between exothermic and endothermic reactions?", "answer": "Exothermic releases heat, endothermic absorbs heat", "topic": "Energetics", "year": "2019"},
        {"question": "Product when acid reacts with base?", "answer": "Salt and water", "topic": "Acids and Bases", "year": "2019"},
        {"question": "Electronic configuration of Sodium (atomic number 11)?", "answer": "2, 8, 1", "topic": "Atomic Structure", "year": "2018"},
        {"question": "Define isomers.", "answer": "Compounds with same molecular formula but different structures", "topic": "Organic Chemistry", "year": "2018"},
        {"question": "Gas produced when zinc reacts with dilute H2SO4?", "answer": "Hydrogen gas H2", "topic": "Reactivity Series", "year": "2017"},
        {"question": "What is a catalyst?", "answer": "Substance that speeds up reaction without being consumed", "topic": "Reaction Kinetics", "year": "2017"},
        {"question": "Difference between saturated and unsaturated hydrocarbons?", "answer": "Saturated have single bonds only, unsaturated have double or triple bonds", "topic": "Organic Chemistry", "year": "2016"},
    ],
    "biology": [
        {"question": "What is the basic unit of life?", "answer": "The cell", "topic": "Cell Biology", "year": "2023"},
        {"question": "State the function of mitochondria.", "answer": "Site of aerobic respiration and ATP production", "topic": "Cell Organelles", "year": "2023"},
        {"question": "What is photosynthesis?", "answer": "Process where plants use sunlight, CO2 and water to produce glucose and oxygen", "topic": "Photosynthesis", "year": "2022"},
        {"question": "Distinguish between mitosis and meiosis.", "answer": "Mitosis produces 2 identical diploid cells. Meiosis produces 4 haploid cells.", "topic": "Cell Division", "year": "2022"},
        {"question": "What is osmosis?", "answer": "Movement of water from high to low concentration through semi-permeable membrane", "topic": "Transport in Cells", "year": "2021"},
        {"question": "Name the four blood groups in ABO system.", "answer": "A, B, AB, O", "topic": "Genetics", "year": "2021"},
        {"question": "What is the role of the kidney?", "answer": "Excretion of waste, osmoregulation and blood pH balance", "topic": "Excretion", "year": "2020"},
        {"question": "Define natural selection.", "answer": "Process where organisms with favourable traits survive and reproduce more", "topic": "Evolution", "year": "2020"},
        {"question": "Function of ribosome?", "answer": "Site of protein synthesis", "topic": "Cell Organelles", "year": "2019"},
        {"question": "What is a food chain? Give Nigerian example.", "answer": "Energy flow from producers to consumers. Example: Grass -> Grasshopper -> Lizard -> Hawk", "topic": "Ecology", "year": "2019"},
        {"question": "State Mendel's Law of Segregation.", "answer": "Alleles separate during gamete formation so each gamete carries one allele", "topic": "Genetics", "year": "2018"},
        {"question": "Difference between arteries and veins?", "answer": "Arteries carry blood away from heart, veins carry blood to heart", "topic": "Circulatory System", "year": "2018"},
        {"question": "Define transpiration.", "answer": "Loss of water vapour from plant leaves through stomata", "topic": "Plant Physiology", "year": "2017"},
        {"question": "Function of white blood cells?", "answer": "Defence against pathogens through phagocytosis and antibody production", "topic": "Immune System", "year": "2017"},
        {"question": "Name the stages of aerobic respiration.", "answer": "Glycolysis, Krebs Cycle, Electron Transport Chain", "topic": "Respiration", "year": "2016"},
    ]
}


def scrape_examguru(subject: str, url: str) -> list:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        questions = []
        for q_block in soup.select(".question-block, .exam-question, .q-item")[:20]:
            q_text = q_block.get_text(strip=True)
            if len(q_text) > 20:
                questions.append({
                    "question": q_text[:500],
                    "answer": "See explanation in textbook",
                    "topic": subject.title(),
                    "year": "2023",
                })
        return questions
    except Exception:
        return []


def build_knowledge_base() -> dict:
    print("Building STEMBridge knowledge base...\n")
    knowledge_base = {}

    for subject, url in SUBJECTS.items():
        print(f"  Processing {subject.title()}...")
        scraped = scrape_examguru(subject, url)

        if len(scraped) >= 5:
            print(f"     Scraped {len(scraped)} questions from web")
            knowledge_base[subject] = scraped
        else:
            print(f"     Using curated WAEC content ({len(FALLBACK_CONTENT[subject])} questions)")
            knowledge_base[subject] = FALLBACK_CONTENT[subject]

        time.sleep(1)

    os.makedirs("data", exist_ok=True)
    with open("data/knowledge_base.json", "w") as f:
        json.dump(knowledge_base, f, indent=2)

    total = sum(len(v) for v in knowledge_base.values())
    print(f"\nKnowledge base ready: {total} questions across {len(knowledge_base)} subjects")
    print("Saved to data/knowledge_base.json")
    return knowledge_base


if __name__ == "__main__":
    build_knowledge_base()