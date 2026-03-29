import logging
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.tools.smtp_tools import SMTPOutreachTool, ToolConfig

logger = logging.getLogger("BurnMonitor")

class BurnMonitor:
    """
    Monitors API burn and user credits.
    Triggers automated alerts via SMTP.
    """
    ALERT_THRESHOLD_CREDITS = 100
    ALERT_THRESHOLD_BALANCE = 5.0

    @classmethod
    def check_and_alert(cls, user_id: str, email: str):
        sql = SQLStore()
        balance_info = sql.get_user_balance(user_id)
        
        balance = balance_info.get("balance", 0.0)
        credits = balance_info.get("credits", 0)
        
        if credits < cls.ALERT_THRESHOLD_CREDITS or balance < cls.ALERT_THRESHOLD_BALANCE:
            logger.warning(f"⚠️ LOW BALANCE ALERT for {user_id}: ${balance} / {credits} credits")
            cls._send_alert_email(email, balance, credits)

    @classmethod
    def _send_alert_email(cls, email: str, balance: float, credits: int):
        smtp = SMTPOutreachTool(ToolConfig(tool_id="burn_alert", name="Alert", description="Burn Alert", parameters_schema={}, allowed_agents=["*"]))
        smtp.execute({
            "recipient": email,
            "subject": "⚠️ Sovereign Matrix: Low Credit Alert",
            "body": f"Your Sovereign Swarm is running low on fuel. \n\nCurrent Balance: ${balance:.2f}\nCredits Remaining: {credits}\n\nPlease top up to avoid matrix suspension."
        })
