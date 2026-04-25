import requests
import time

def test_generate_pulse():
    print("🚀 Triggering INDPlus Executive Pulse (30D window)...")
    url = "http://localhost:8001/api/generate-report?weeks=4&max_reviews=100"
    
    try:
        start_time = time.time()
        response = requests.post(url)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Report ID: {data['report_id']}")
            print(f"⏱️ Duration: {duration:.2f}s")
            
            # Check if report exists in DB
            r_url = f"http://localhost:8001/api/reports/{data['report_id']}"
            r_resp = requests.get(r_url)
            report = r_resp.json()
            
            print(f"📊 Themes Found: {len(report.get('themes', []))}")
            print(f"📄 PDF Path: {report.get('pdf_path')}")
            print(f"📧 Email Draft Length: {len(report.get('email_body', ''))} chars")
            
            if report.get('pdf_path'):
                print("💎 PDF Generation Verified.")
            else:
                print("⚠️ PDF Path Missing from report data.")
        else:
            print(f"❌ Failed! Status: {response.status_code}")
            print(f"📝 Detail: {response.text}")
            
    except Exception as e:
        print(f"🚨 Error: {e}")

if __name__ == "__main__":
    test_generate_pulse()
