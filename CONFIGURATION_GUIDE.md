# 🔧 Drishti Configuration Guide

## Current System Status

### ✅ Working Features (Demo Mode)
- ✅ Login/Authentication
- ✅ Dashboard UI
- ✅ Network Graph Visualization  
- ✅ Chat Interface
- ✅ PDF Export
- ✅ Audit Logs

### ⚠️ Using Mock/Hardcoded Data
- ⚠️ **Chatbot responses** - Returns "[Mock] Evaluated prompt..." 
- ⚠️ **Dashboard statistics** - Hardcoded numbers
- ⚠️ **Network analysis** - Generic placeholder data
- ⚠️ **Crime predictions** - Sample forecasts

---

## 🤖 Why is the Chatbot Not Human-Like?

The chatbot currently shows **"[Mock] Evaluated prompt..."** because:

1. **Mistral AI API Key is Missing**
   - Location: `backend/.env` file
   - Variable: `MISTRAL_API_KEY`
   - Current value: Empty (not configured)
   
2. **No Real Crime Database**
   - System needs actual crime records
   - ChromaDB vector database is empty
   - RAG pipeline has no data to retrieve

---

## 🚀 How to Enable Real AI Responses

### Step 1: Get Mistral AI API Key (FREE)

1. **Go to**: https://console.mistral.ai/
2. **Sign up** for free account
3. **Create API Key**:
   - Navigate to "API Keys" section
   - Click "Create new secret key"
   - Copy the key (starts with something like `sk-...`)

### Step 2: Configure Backend

1. **Open** `backend/.env` file
2. **Add your key**:
   ```env
   MISTRAL_API_KEY=sk-your-actual-mistral-api-key-here
   ```
3. **Save the file**

### Step 3: Restart Backend Server

The backend will automatically detect the API key and start using real AI!

---

## 📊 Understanding Current Data Flow

### Chat Without API Key (Current):
```
User: "Tell me about crime trends"
  ↓
System: Checks MISTRAL_API_KEY
  ↓
Key Missing → Returns: "[Mock] Evaluated prompt: Context: ... User Query: Tell me about crime trends"
```

### Chat With API Key (After Configuration):
```
User: "Tell me about crime trends"
  ↓
System: Checks MISTRAL_API_KEY → Found!
  ↓
RAG Pipeline: Retrieves relevant crime records from ChromaDB
  ↓
Mistral AI: Analyzes context + user query
  ↓
Returns: "Based on the crime data from Karnataka State Police, I can see that theft incidents have increased by 15% in Bengaluru Urban district over the past 30 days. The main hotspots are..."
```

---

## 🗄️ Network Analysis - What It Shows

The **Criminal Network Analysis** currently displays:
- **Mock connections** between generic nodes
- **No real names** or case details
- **No actual relationship data**

### To Enable Real Network Analysis:

You need to populate the database with actual crime records that include:
- Suspect names
- Associated persons
- Crime IDs
- Relationships (accomplice, witness, victim, etc.)

---

## 💡 Quick Test to Verify AI is Working

After adding Mistral API key:

1. **Restart backend** server
2. **Go to Chat** page
3. **Type**: "Hello, who are you?"
4. **Expected Response** (if working):
   ```
   "Hello! I'm Drishti, an AI assistant for Karnataka State Police. 
   I'm here to help you with crime data analysis, network investigation, 
   and insights from police records. How can I assist you today?"
   ```

5. **If still seeing** `[Mock] Evaluated prompt...`:
   - Check: API key is correct in `.env`
   - Check: Backend server was restarted
   - Check: No spaces around the API key in `.env`

---

## 🔐 Security Notes

⚠️ **IMPORTANT**:
- Never commit `.env` file to Git (already in `.gitignore`)
- Keep your Mistral API key private
- Change JWT_SECRET_KEY in production
- Use environment variables in production deployment

---

## 📈 Data Population Options

### Option 1: Use Synthetic Data (For Demo)
```bash
cd backend
python data/generate_synthetic_data.py
```

### Option 2: Connect Real Database
Configure PostgreSQL connection in `.env`:
```env
DATABASE_URL=postgresql://user:password@host:port/database
```

### Option 3: Import CSV Data
Create import script to load crime records into ChromaDB

---

## 🎯 Feature Checklist

### Fully Working (No Configuration Needed)
- [x] User Authentication
- [x] JWT Token Management
- [x] Rate Limiting
- [x] Session Management
- [x] UI Components
- [x] PDF Export (generates basic reports)

### Needs Configuration
- [ ] **AI Chat** (needs Mistral API key)
- [ ] Real Crime Database (needs data import)
- [ ] Network Analysis with real data
- [ ] Crime Predictions with real data
- [ ] Translation (needs Google Translate API key - optional)

---

## 📞 Support

**System is working correctly** - it's just in **demo mode** without API keys.

Once you add the Mistral API key, you'll get:
- ✅ Intelligent, context-aware responses
- ✅ Natural conversation flow
- ✅ Crime data analysis
- ✅ Insight generation

**Current Cost**: Mistral offers a **free tier** perfect for hackathons and testing!

---

**Last Updated**: January 2026  
**Status**: Ready for API Key Configuration
