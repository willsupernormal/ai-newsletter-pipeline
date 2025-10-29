# Documentation Index

> **Complete documentation for the AI Newsletter Pipeline**

**Last Updated:** October 29, 2025

---

## 📚 **All Documentation**

### **Essential Docs** (Start Here)

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[../START_HERE.md](../START_HERE.md)** | Project overview & navigation | 10 min |
| **[SETUP.md](SETUP.md)** | Complete setup from scratch | 30 min |
| **[OPERATIONS.md](OPERATIONS.md)** | Daily operations & troubleshooting | 20 min |

### **Reference Docs**

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[../README.md](../README.md)** | Technical architecture | 15 min |
| **[../PROJECT_STATUS.md](../PROJECT_STATUS.md)** | Current state & known issues | 10 min |
| **[../AIRTABLE_DATA_SPEC.md](../AIRTABLE_DATA_SPEC.md)** | Data structure reference | 15 min |

### **Specialized Guides**

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)** | CI/CD configuration | 10 min |
| **[LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md)** | Testing locally | 5 min |
| **[AIRTABLE_COMPLETE_SETUP.md](AIRTABLE_COMPLETE_SETUP.md)** | Detailed Airtable setup | 20 min |

---

## 🎯 **Quick Links by Task**

### **"I'm new to this project"**
1. Read [../START_HERE.md](../START_HERE.md)
2. Read [../README.md](../README.md)
3. Read [SETUP.md](SETUP.md)

### **"I need to set up from scratch"**
1. Read [SETUP.md](SETUP.md)
2. Follow step-by-step instructions
3. Test with [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md)

### **"I need to run/maintain the system"**
1. Read [OPERATIONS.md](OPERATIONS.md)
2. Check [../PROJECT_STATUS.md](../PROJECT_STATUS.md)
3. Use troubleshooting section as needed

### **"I need to understand the data"**
1. Read [../AIRTABLE_DATA_SPEC.md](../AIRTABLE_DATA_SPEC.md)
2. Check Supabase schema in [SETUP.md](SETUP.md)
3. Review code in `database/` directory

### **"I need to debug an issue"**
1. Check [../PROJECT_STATUS.md](../PROJECT_STATUS.md) for known issues
2. Use [OPERATIONS.md](OPERATIONS.md) troubleshooting section
3. Check relevant logs (GitHub Actions, Railway, Supabase)

### **"I need to modify the code"**
1. Read [../README.md](../README.md) for architecture
2. Review relevant code directory
3. Test with [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md)

---

## 📖 **Documentation Structure**

```
docs/
├── README.md (this file)           ← Documentation index
├── SETUP.md                        ← Complete setup guide
├── OPERATIONS.md                   ← Daily operations & troubleshooting
├── GITHUB_ACTIONS_SETUP.md         ← CI/CD configuration
├── LOCAL_TESTING_GUIDE.md          ← Testing locally
└── AIRTABLE_COMPLETE_SETUP.md      ← Detailed Airtable setup

Root directory:
├── START_HERE.md                   ← Project overview (read first!)
├── README.md                       ← Technical architecture
├── PROJECT_STATUS.md               ← Current state & issues
└── AIRTABLE_DATA_SPEC.md           ← Data structure reference
```

---

## ✅ **Documentation Checklist**

### **For New Users:**
- [ ] Read START_HERE.md
- [ ] Read README.md
- [ ] Read PROJECT_STATUS.md
- [ ] Read SETUP.md
- [ ] Complete setup steps
- [ ] Test locally

### **For Operators:**
- [ ] Bookmark OPERATIONS.md
- [ ] Bookmark PROJECT_STATUS.md
- [ ] Know where to find logs
- [ ] Understand troubleshooting steps

### **For Developers:**
- [ ] Read README.md architecture
- [ ] Read AIRTABLE_DATA_SPEC.md
- [ ] Review code structure
- [ ] Understand data flow

---

## 🔄 **Keeping Documentation Updated**

### **When to Update:**

**SETUP.md:**
- New environment variables added
- Setup steps change
- New external services added

**OPERATIONS.md:**
- New operational procedures
- New troubleshooting steps
- New maintenance tasks

**PROJECT_STATUS.md:**
- System state changes
- New issues discovered
- Issues resolved

**README.md:**
- Architecture changes
- New features added
- Tech stack changes

### **How to Update:**

1. Edit the relevant markdown file
2. Update "Last Updated" date
3. Commit with clear message
4. Test any code examples

---

## 📞 **Need Help?**

1. **Check documentation first** - Most questions are answered here
2. **Check PROJECT_STATUS.md** - For known issues
3. **Check logs** - GitHub Actions, Railway, Supabase
4. **Review code** - Comments and docstrings explain logic

---

**Happy documenting! 📚**

