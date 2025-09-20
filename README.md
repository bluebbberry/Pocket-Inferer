# ACE Logic Calculator with APE Integration

A powerful desktop application for logical reasoning using **Attempto Controlled English (ACE)**, now integrated with the official **APE (Attempto Parsing Engine)** HTTP API for robust natural language understanding and logical inference.

## Features

- **APE Integration**: Uses the official Attempto Parsing Engine via HTTP API for accurate parsing
- **Dual Interface**: Calculator mode for quick logic problems, Programming mode for complex projects
- **AI Translation**: Convert natural language to ACE using Ollama (optional)
- **Visual Results**: See DRS (Discourse Representation Structure), paraphrases, and OWL output
- **CSV Import**: Load data from CSV files with intelligent ACE mapping
- **Syntax Highlighting**: Code editor with ACE syntax highlighting
- **File Management**: Project-based file management in Programming mode

## Prerequisites

### Required Components

1. **Python 3.8+** with tkinter support
2. **APE (Attempto Parsing Engine)** - The core reasoning engine
3. **SWI-Prolog** - Required for APE compilation

### Optional Components

4. **Ollama** - For AI-powered natural language translation
5. **Mistral or similar LLM** - Running in Ollama for translation features

## Installation & Setup

### Step 1: Install SWI-Prolog

**Windows:**
```bash
# Download from https://www.swi-prolog.org/download/stable
# Install with clib, sgml, http, and pldoc packages
```

**Ubuntu/Debian:**
```bash
sudo apt-get install swi-prolog swi-prolog-packages
```

**macOS:**
```bash
brew install swi-prolog
```

### Step 2: Download and Compile APE

```bash
# Download APE
wget http://attempto.ifi.uzh.ch/site/releases/ape-6.7-131003.tar.gz
tar -xzf ape-6.7-131003.tar.gz
cd ape-6.7-131003

# Compile APE
# Windows:
make_exe.bat

# Unix/Linux/macOS:
make install
```

### Step 3: Start APE HTTP Server

```bash
# Start APE server on default port 8000
./ape.exe -httpserver

# Or specify custom port:
./ape.exe -httpserver -port 8001
```

**Important**: Keep the APE server running while using the calculator. You should see:
```
% Started server at http://localhost:8000/
```

### Step 4: Install Python Dependencies

```bash
pip install requests tkinter
```

### Step 5: Optional - Setup Ollama for AI Translation

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull a language model
ollama pull mistral

# Start Ollama (usually runs automatically)
ollama serve
```

## Usage

### Starting the Application

```bash
python ace_calculator_ape.py
```

### Calculator Mode (Default)

Perfect for quick logical reasoning tasks:

1. **Enter ACE statements** in the text area
2. **Click "PARSE WITH APE"** to analyze and reason
3. **View results** including DRS structures and query answers
4. **Use templates** for common statement types

### Programming Mode

For complex projects and file management:

1. **Click "Programming Mode"** button
2. **Create/open ACE files** using the file explorer
3. **Edit with syntax highlighting** in the code editor
4. **Parse entire files** with APE integration

## Exciting ACE Examples

### 1. Basic Logical Reasoning

```ace
# Facts about people
Every man is a person.
Every woman is a person.
John is a man.
Mary is a woman.

# Properties
John is tall.
Mary is intelligent.
Every tall person is confident.

# Queries
Is John a person?          # → Yes
Is John confident?         # → Yes
Who is intelligent?        # → Mary
```

### 2. Complex Relationships

```ace
# Family relationships with transitivity
John is the father of Mary.
Mary is the mother of Peter.
Tom is the father of John.

# Rules for family relations
If X is the father of Y then X is a parent of Y.
If X is the mother of Y then X is a parent of Y.
If X is a parent of Y and Y is a parent of Z then X is a grandparent of Z.

# Queries
Who is a parent of Mary?           # → John
Who is a grandparent of Peter?     # → John, Tom (depending on rule application)
Is Tom a grandparent of Peter?     # → Yes
```

### 3. Conditional Logic with Emotions

```ace
# Emotional states and preferences
John likes chocolate.
Mary likes books.
Peter likes music.
Sarah likes chocolate.

# Conditional rules
Every person that likes chocolate is happy.
Every person that likes books is wise.
If a person X is happy and a person Y is wise then X admires Y.

# Complex emotional rules
If a person X likes the same thing as a person Y then X and Y are friends.

# Queries
Who is happy?              # → John, Sarah
Who is wise?              # → Mary
Who are friends?          # → John and Sarah
Does John admire Mary?    # → Yes (John is happy, Mary is wise)
```

### 4. Business Logic - Employee Management

```ace
# Employee facts
John is an employee.
Mary is an employee.
Peter is a manager.
Every manager is an employee.

# Skills and qualifications
John has skill programming.
Mary has skill design.
Peter has skill leadership.
John has experience 5.
Mary has experience 3.

# Business rules
Every employee that has experience more-than 4 is senior.
Every senior employee is eligible-for promotion.
If an employee X has skill leadership then X can-manage projects.

# Queries
Who is senior?                    # → John
Who is eligible-for promotion?    # → John
Who can-manage projects?         # → Peter
```

### 5. Medical Diagnosis Logic

```ace
# Patient symptoms
Patient-123 has symptom fever.
Patient-123 has symptom cough.
Patient-123 has symptom fatigue.

Patient-456 has symptom headache.
Patient-456 has symptom nausea.

# Diagnostic rules
If a patient X has symptom fever and X has symptom cough then X has condition flu.
If a patient X has symptom headache and X has symptom nausea then X has condition migraine.
Every patient that has condition flu needs treatment rest.
Every patient that has condition migraine needs treatment medication.

# Treatment rules
If a patient X needs treatment Y then X should-receive Y.

# Queries
What condition does Patient-123 have?     # → flu
What condition does Patient-456 have?     # → migraine
What treatment does Patient-123 need?     # → rest
Who should-receive medication?            # → Patient-456
```

### 6. University Course Prerequisites

```ace
# Course structure
Course-Math101 is a course.
Course-CS101 is a course.
Course-CS201 is a course.
Course-CS301 is a course.

# Students and enrollments
Alice is a student.
Bob is a student.
Alice completed Course-Math101.
Bob completed Course-Math101.
Bob completed Course-CS101.

# Prerequisite rules
Course-CS101 requires Course-Math101.
Course-CS201 requires Course-CS101.
Course-CS301 requires Course-CS201.

# Enrollment rules
If a student X completed a course Y and course Z requires course Y then X is-eligible-for course Z.
Every student that is-eligible-for a course can-enroll-in that course.

# Queries
What course can Alice enroll-in?      # → Course-CS101
What course can Bob enroll-in?        # → Course-CS201
Is Alice eligible-for Course-CS201?   # → No
Is Bob eligible-for Course-CS301?     # → No
```

### 7. Supply Chain Logic

```ace
# Supply chain entities
Factory-A is a supplier.
Factory-B is a supplier.
Warehouse-X is a distributor.
Store-Y is a retailer.

# Product flow
Factory-A produces Product-Widget.
Factory-B produces Product-Gadget.
Warehouse-X stocks Product-Widget.
Warehouse-X stocks Product-Gadget.

# Supply chain rules
If a supplier X produces a product Y and a distributor Z stocks product Y then X supplies Z.
If a distributor X stocks a product Y and a retailer Z sells product Y then X supplies Z.
Every product that is-supplied-by multiple suppliers is available.

# Inventory rules
Store-Y sells Product-Widget.
If a product X is available and a retailer Y sells product X then Y has-inventory-of X.

# Queries
Who supplies Warehouse-X?           # → Factory-A, Factory-B
What does Store-Y have-inventory-of? # → Product-Widget
Is Product-Widget available?        # → Yes
```

## APE Server Configuration

### Default Configuration
- **Port**: 8000
- **URL**: http://localhost:8000

### Custom Configuration
```bash
# Different port
./ape.exe -httpserver -port 9000

# The calculator will auto-detect the server or you can modify the APEClient class
```

### Testing APE Server
```bash
# Test if server is running
curl "http://localhost:8000/?text=John is happy.&solo=drspp"
```

## Troubleshooting

### APE Server Issues
1. **"APE server not available"**
   - Ensure APE server is running: `./ape.exe -httpserver`
   - Check firewall settings for port 8000
   - Verify SWI-Prolog installation

2. **Compilation errors**
   - Install all required SWI-Prolog packages: `clib`, `sgml`, `http`, `pldoc`
   - Check make permissions on Unix systems

### Application Issues
1. **Import errors**
   - Ensure Python 3.8+ is installed
   - Install missing packages: `pip install requests`

2. **AI Translation not working**
   - Ollama is optional - basic fallback translation will work
   - Check if Ollama is running: `ollama list`

## ACE Language Reference

### Basic Patterns

**Facts:**
- `John is happy.`
- `Mary likes chocolate.`
- `Every person is mortal.`

**Rules:**
- `If X likes chocolate then X is happy.`
- `Every person that is happy smiles.`

**Queries:**
- `Is John happy?`
- `Who is happy?`
- `What does Mary like?`

### Advanced Constructs
- **Negation**: `John does not like vegetables.`
- **Conditionals**: `If X is tired then X sleeps.`
- **Quantification**: `Every`, `Some`, `No`
- **Relations**: `X is the father of Y`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test with APE server integration
4. Submit a pull request

## License

This project integrates with APE (Attempto Parsing Engine) which has its own license terms. Please review the APE documentation for usage restrictions.

## Links

- **APE Website**: http://attempto.ifi.uzh.ch
- **SWI-Prolog**: https://www.swi-prolog.org
- **Ollama**: https://ollama.ai
- **ACE Language Guide**: http://attempto.ifi.uzh.ch/site/docs/

## Support

For APE-related issues, consult the Attempto community mailing list at:
http://attempto.ifi.uzh.ch/site/mailinglist/

---

*Experience the power of controlled natural language reasoning with formal logical precision!*