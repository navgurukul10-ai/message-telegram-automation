# 🎯 Job Quality Scoring System

## Overview
The Job Quality Scoring System automatically evaluates job postings and assigns them a quality score from 0 to 100 based on the completeness and usefulness of the information provided.

## Scoring Criteria

### Points Breakdown

| Criteria | Points | Description |
|----------|--------|-------------|
| **Company Name** | 20 | Presence of a recognizable company name |
| **Salary Information** | 20 | Salary/CTC/Package mentioned |
| **Apply Link** | 20 | Valid URL to apply (not email) |
| **Location** | 15 | Job location specified |
| **Skills/Requirements** | 15 | Skills or requirements mentioned |
| **Remote/WFH** | 10 | Remote or Work From Home option |

**Maximum Score:** 100 points

### Best Jobs Threshold
Jobs with a score of **60 or above** are classified as "Best Jobs" and displayed in the "Best Quality Jobs" section of the dashboard.

## Special Rules

### 🌍 International Jobs (STRICT RULE)
For jobs located **outside India**, having **Remote/WFH option is MANDATORY**:
- If an international job is **NOT remote**, the score is **immediately set to 0** (DISQUALIFIED)
- This ensures that **ONLY** remote international opportunities are shown in Best Jobs
- Non-remote international jobs will **NEVER** appear in Best Jobs, regardless of other qualities

### 📍 Location Detection
The system recognizes:
- **Indian cities**: Bangalore, Mumbai, Delhi NCR, Pune, Hyderabad, Chennai, etc.
- **International locations**: USA, UK, Singapore, Dubai, Canada, Australia, etc.

### 🔗 Apply Link Validation
- Only **real URLs** are counted (http://, https://, www.)
- Email addresses are **NOT** counted as apply links
- Ensures users can directly apply via a web link

## Examples

### Example 1: Perfect Job (100 points)
```
Software Engineer - Python Backend
Company: Tech Solutions Pvt Ltd
Location: Bangalore, India
Salary: 12-18 LPA
Skills: Python, Django, PostgreSQL, AWS
Work Mode: Hybrid (3 days WFH)
Apply: https://techsolutions.com/careers/se-python
```
**Score Breakdown:**
- Company Name: ✅ 20
- Salary: ✅ 20
- Apply Link: ✅ 20
- Location: ✅ 15
- Skills: ✅ 15
- Remote/Hybrid: ✅ 10
**Total: 100/100**

### Example 2: Good Job (75 points)
```
Marketing Manager
Company: StartupXYZ
Location: Remote (India)
Skills: Digital Marketing, SEO, Content Strategy
Salary: Not disclosed
Apply: careers@startupxyz.com
```
**Score Breakdown:**
- Company Name: ✅ 20
- Salary: ❌ 0
- Apply Link: ❌ 0 (email, not URL)
- Location: ✅ 15
- Skills: ✅ 15
- Remote: ✅ 10
**Total: 60/100** (Qualifies as Best Job!)

### Example 3: Below Threshold (50 points)
```
Hiring for Sales Executive
Location: Mumbai
Experience: 2-5 years
Contact: +91-9876543210
```
**Score Breakdown:**
- Company Name: ❌ 0
- Salary: ❌ 0
- Apply Link: ❌ 0
- Location: ✅ 15
- Skills: ❌ 0
- Remote: ❌ 0
**Total: 15/100** (Not shown in Best Jobs)

### Example 4: International Remote Job (80 points)
```
Senior Developer - Remote
Company: GlobalTech Inc
Location: USA (Remote worldwide)
Salary: $80,000 - $120,000
Skills: React, Node.js, TypeScript
Apply: https://globaltech.com/apply/senior-dev
```
**Score Breakdown:**
- Company Name: ✅ 20
- Salary: ✅ 20
- Apply Link: ✅ 20
- Location: ✅ 15
- Skills: ✅ 15
- Remote: ✅ 10
**Total: 100/100**

### Example 5: International On-site Job (DISQUALIFIED)
```
Frontend Developer
Company: London Startups Ltd
Location: London, UK (On-site only)
Salary: £50,000
Skills: Vue.js, CSS, HTML
Apply: https://londonstartups.uk/careers
```
**Score Breakdown:**
- Company Name: ✅ 20
- Salary: ✅ 20
- Apply Link: ✅ 20
- Location: ✅ 15 (International)
- Skills: ✅ 15
- Remote: ❌ 0
- **DISQUALIFIED:** International job without remote option
**Total: 0/100** ❌ (NOT shown in Best Jobs)

## Pattern Recognition

### Company Name Patterns
- Keywords: "Company", "Organization", "Technologies", "Solutions", "Systems", "Labs", "Studios", etc.
- Examples: "ABC Technologies", "XYZ Solutions Pvt Ltd"

### Salary Patterns
- Formats recognized:
  - `12 LPA`, `10-15 lakhs`
  - `₹50,000`, `Rs. 8 LPA`
  - `$80,000`, `$60k-$90k`
  - `CTC: 15 LPA`, `Package: 12-18L`

### Location Patterns
- Indian cities by name
- International countries/cities
- Keywords: "Location:", "Based in:", "Office in:"

### Skills Patterns
- Technical: Python, Java, React, AWS, Docker, SQL, etc.
- Non-technical: Marketing, Sales, Leadership, Design, etc.
- Keywords: "Skills:", "Technologies:", "Experience in:"

### Remote Patterns
- Keywords: Remote, WFH, Work from home, Hybrid

## Benefits

1. **🎯 Quality Filter**: Only high-quality, complete job postings are shown in "Best Jobs"
2. **⏱️ Time Saving**: Users don't waste time on incomplete job postings
3. **🌐 Remote Focus**: International jobs are filtered to show only remote opportunities
4. **📊 Transparency**: Clear scoring helps users understand why a job is featured
5. **🔄 Dynamic**: Works for both Tech and Non-Tech jobs equally

## Technical Implementation

### API Endpoint
`GET /api/best_jobs`

Returns top 50 jobs with score >= 60, sorted by score (highest first).

### Response Format
```json
{
  "message": "Full job description text",
  "company": "Extracted company name",
  "skills": "Extracted skills",
  "salary": "Extracted salary info",
  "work_mode": "Remote/On-site",
  "location": "Extracted location",
  "score": 85,
  "date": "2025-10-07",
  "group": "Job Group Name",
  "apply_link": "https://apply-link.com"
}
```

## Future Enhancements

Potential improvements for the scoring system:
1. **Machine Learning**: Train a model to better extract company names and skills
2. **Company Verification**: Verify company legitimacy via LinkedIn/web search
3. **Salary Normalization**: Convert all salaries to a standard format for comparison
4. **Experience Level**: Score based on seniority (Fresher/Mid/Senior)
5. **Application Deadline**: Bonus points for mentioning deadline
6. **User Feedback**: Allow users to rate jobs and adjust scoring algorithm

## Conclusion

The Job Quality Scoring System ensures that users see the most complete, relevant, and actionable job opportunities first, saving time and improving the job search experience! 🚀

