import sys
import os
from collections import Counter

sys.path.append(os.getcwd())
from orchestrator.src.memory.sql_store import SQLStore, AnalyticsEvent

def generate_revenue_report():
    print("📊 REALMS2RICHES REVENUE & CONVERSION REPORT 📊")
    print("==============================================")
    
    sql = SQLStore()
    session = sql.Session()
    
    try:
        events = session.query(AnalyticsEvent).all()
        
        print(f"Total Events Tracked: {len(events)}")
        
        # 1. Funnel Performance
        type_counts = Counter([e.event_type for e in events])
        print("\n[Funnel Breakdown]")
        for etype, count in type_counts.items():
            print(f" - {etype}: {count}")
            
        # 2. Top Products by View
        view_counts = Counter([e.product_id for e in events if e.event_type == 'PRODUCT_VIEW' and e.product_id])
        print("\n[Top Products by Views]")
        for pid, count in view_counts.most_common(5):
            print(f" - {pid}: {count} views")
            
        # 3. Conversion Rate (Checkout Completed / Checkout Started)
        started = type_counts.get('CHECKOUT_STARTED', 0)
        completed = type_counts.get('CHECKOUT_COMPLETED', 0)
        cr = (completed / started * 100) if started > 0 else 0
        print(f"\n[Checkout Conversion Rate]: {cr:.2f}%")
        
        # 4. Campaign Performance
        campaign_sends = Counter([e.campaign_id for e in events if e.event_type == 'EMAIL_SENT' and e.campaign_id])
        print("\n[Outreach Campaign Performance (Sends)]")
        for cid, count in campaign_sends.items():
            print(f" - {cid}: {count} emails sent")

    finally:
        session.close()

if __name__ == "__main__":
    generate_revenue_report()
