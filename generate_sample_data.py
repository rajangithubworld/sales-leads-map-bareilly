"""
Generate a sample Excel file with company data in Bareilly for testing.
Run this once: python generate_sample_data.py
"""
import pandas as pd

data = [
    {
        "Company": "Bareilly Agro Industries",
        "Address": "Civil Lines, Bareilly",
        "Contact_Person": "Rajesh Kumar",
        "Designation": "Managing Director",
        "Phone": "+91 98370 12345",
        "Email": "rajesh@bareillyagro.com",
    },
    {
        "Company": "Rohilkhand Polymers Pvt Ltd",
        "Address": "Rampur Garden, Bareilly",
        "Contact_Person": "Sunil Verma",
        "Designation": "General Manager",
        "Phone": "+91 94120 56789",
        "Email": "sunil.verma@rohilkhandpoly.in",
    },
    {
        "Company": "Nath Furniture House",
        "Address": "Kutub Khana, Bareilly",
        "Contact_Person": "Amit Nath",
        "Designation": "Proprietor",
        "Phone": "+91 89790 11223",
        "Email": "amit@nathfurniture.com",
    },
    {
        "Company": "Shivam Textiles",
        "Address": "Subhash Nagar, Bareilly",
        "Contact_Person": "Priya Sharma",
        "Designation": "CEO",
        "Phone": "+91 70608 44556",
        "Email": "priya@shivamtextiles.in",
    },
    {
        "Company": "Bareilly Auto Components",
        "Address": "Pilibhit Bypass, Bareilly",
        "Contact_Person": "Vikram Singh",
        "Designation": "Plant Head",
        "Phone": "+91 99270 77889",
        "Email": "vikram.singh@bareillyauto.com",
    },
    {
        "Company": "Ganga Dairy Products",
        "Address": "CB Ganj, Bareilly",
        "Contact_Person": "Meena Agarwal",
        "Designation": "Director",
        "Phone": "+91 85218 99001",
        "Email": "meena@gangadairy.in",
    },
    {
        "Company": "Rohit Packaging Solutions",
        "Address": "Izatnagar, Bareilly",
        "Contact_Person": "Rohit Gupta",
        "Designation": "Owner",
        "Phone": "+91 63880 22334",
        "Email": "rohit@rohitpackaging.com",
    },
    {
        "Company": "Kashi Electricals",
        "Address": "Rajendra Nagar, Bareilly",
        "Contact_Person": "Deepak Kashyap",
        "Designation": "Sales Manager",
        "Phone": "+91 77520 55667",
        "Email": "deepak@kashielectricals.in",
    },
    {
        "Company": "Bareilly Steel Corporation",
        "Address": "Nawabganj, Bareilly",
        "Contact_Person": "Alok Tiwari",
        "Designation": "VP Operations",
        "Phone": "+91 94568 88990",
        "Email": "alok.tiwari@bareillysteel.com",
    },
    {
        "Company": "Surya Pharma Ltd",
        "Address": "Satellite Hospital Road, Bareilly",
        "Contact_Person": "Dr. Neha Singh",
        "Designation": "Chief Pharmacist",
        "Phone": "+91 88009 11234",
        "Email": "neha@suryapharma.in",
    },
]

df = pd.DataFrame(data)
df.to_excel("sample_companies.xlsx", index=False)
print(f"✅ Created sample_companies.xlsx with {len(df)} companies")
print(df[["Company", "Address"]].to_string(index=False))
