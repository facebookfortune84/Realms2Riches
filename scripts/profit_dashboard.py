import time
import os
import sys
from datetime import datetime
from orchestrator.src.memory.sql_store import SQLStore

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_dashboard():
    sql = SQLStore()
    
    while True:
        clear_screen()
        profit = sql.get_total_profit()
        
        # Query ledger for stats
        session = sql.Session()
        from orchestrator.src.memory.sql_store import ProfitRecord
        entries = session.query(ProfitRecord).all()
        revenue = sum([e.amount for e in entries if e.type == 'revenue'])
        api_costs = sum([e.amount for e in entries if e.category == 'api_cost'])
        fees = sum([e.amount for e in entries if e.category == 'fee'])
        session.close()

        print("====================================================")
        print("   💎 REALMS2RICHES SOVEREIGN PROFIT BOARD 💎")
        print("====================================================")
        print(f" TIME:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" STATUS:  {'🟢 PROFITABLE' if profit > 0 else '🔴 BURN MODE'}")
        print("----------------------------------------------------")
        print(f" GROSS REVENUE:  ${revenue:,.4f}")
        print(f" API BURN:       -${api_costs:,.4f}")
        print(f" TRANSACTION FEES: -${fees:,.4f}")
        print("----------------------------------------------------")
        print(f" NET PROFIT:     ${profit:,.4f}")
        print("====================================================")
        print(" [CTRL+C] to Exit Dashboard (Backend will keep running)")
        
        time.sleep(5)

if __name__ == "__main__":
    try:
        show_dashboard()
    except KeyboardInterrupt:
        sys.exit(0)
