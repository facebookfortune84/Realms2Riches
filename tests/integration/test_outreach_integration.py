import pytest
import os
import json
import asyncio
from unittest.mock import patch, MagicMock
from orchestrator.src.tools.smtp_tools import SMTPOutreachTool
from orchestrator.src.validation.schemas import ToolInvocation, ToolConfig
from orchestrator.src.core.outreach.config import outreach_settings
from orchestrator.src.core.config import settings
import smtplib

@pytest.fixture(autouse=True)
def setup_outreach_test_env():
    """Set up environment variables for outreach testing and reset after."""
    original_outreach_enabled = os.environ.get("OUTREACH_ENABLED")
    original_dry_run_mode = os.environ.get("DRY_RUN_MODE")
    original_test_recipient = os.environ.get("OUTREACH_TEST_RECIPIENT")
    original_smtp_user = os.environ.get("SMTP_USER")
    original_smtp_pass = os.environ.get("SMTP_PASS")

    os.environ["OUTREACH_ENABLED"] = "True"
    os.environ["DRY_RUN_MODE"] = "True" # Force dry run
    os.environ["OUTREACH_TEST_RECIPIENT"] = "test@example.com"
    os.environ["SMTP_USER"] = "mock_sender@example.com"
    os.environ["SMTP_PASS"] = "mock_password"

    # Re-instantiate settings to pick up new env vars


    yield

    # Clean up environment variables
    if original_outreach_enabled is not None: os.environ["OUTREACH_ENABLED"] = original_outreach_enabled
    else: del os.environ["OUTREACH_ENABLED"]
    if original_dry_run_mode is not None: os.environ["DRY_RUN_MODE"] = original_dry_run_mode
    else: del os.environ["DRY_RUN_MODE"]
    if original_test_recipient is not None: os.environ["OUTREACH_TEST_RECIPIENT"] = original_test_recipient
    else: del os.environ["OUTREACH_TEST_RECIPIENT"]
    if original_smtp_user is not None: os.environ["SMTP_USER"] = original_smtp_user
    else: del os.environ["SMTP_USER"]
    if original_smtp_pass is not None: os.environ["SMTP_PASS"] = original_smtp_pass
    else: del os.environ["SMTP_PASS"]




@patch('smtplib.SMTP_SSL')
@patch('smtplib.SMTP')
def test_outreach_dry_run_mode(mock_smtp, mock_smtp_ssl, setup_outreach_test_env, caplog):
    """
    Test that emails are not sent in dry-run mode and planned actions are logged.
    """
    tool = SMTPOutreachTool(ToolConfig(tool_id="smtp_outreach_test", name="SMTP Outreach Test", description="Test", parameters_schema={}, allowed_agents=["*"]))
    invocation = ToolInvocation(
        tool_id="smtp_outreach",
        input_data={
            "target_email": "real_target@example.com",
            "subject": "Test Subject",
            "html_body": "Test Body with <a href='https://example.com/unsubscribe'>unsubscribe</a>"
        }
    )

    with caplog.at_level(outreach_settings.logger.info):
        result = tool.execute(invocation)
    
    # Assert no actual SMTP connection was made
    mock_smtp.assert_not_called()
    mock_smtp_ssl.assert_not_called()

    assert result["status"] == "success" # Dry run is still a 'success' in terms of execution flow
    assert result["target"] == outreach_settings.OUTREACH_TEST_RECIPIENT

    # Verify logging for dry run
    assert "DRY_RUN: Rerouting outreach from real_target@example.com to test@example.com" in caplog.text
    assert "DISPATCHING SMTP OUTREACH TO test@example.com" in caplog.text


@patch('smtplib.SMTP_SSL')
@patch('smtplib.SMTP')
def test_outreach_disabled_mode(mock_smtp, mock_smtp_ssl, setup_outreach_test_env, caplog):
    """
    Test that no actions are taken when OUTREACH_ENABLED is False.
    """
    os.environ["OUTREACH_ENABLED"] = "False"


    tool = SMTPOutreachTool(ToolConfig(tool_id="smtp_outreach_test", name="SMTP Outreach Test", description="Test", parameters_schema={}, allowed_agents=["*"]))
    invocation = ToolInvocation(
        tool_id="smtp_outreach",
        input_data={
            "target_email": "real_target@example.com",
            "subject": "Test Subject",
            "html_body": "Test Body"
        }
    )

    with caplog.at_level(outreach_settings.logger.warning):
        result = tool.execute(invocation)
    
    # Assert no actual SMTP connection was made
    mock_smtp.assert_not_called()
    mock_smtp_ssl.assert_not_called()

    assert result["status"] == "simulated"
    assert "OUTREACH DISABLED: Simulation only for real_target@example.com" in caplog.text

def test_malformed_email_rejected(setup_outreach_test_env):
    """Test that malformed emails are rejected."""
    tool = SMTPOutreachTool(ToolConfig(tool_id="smtp_outreach_test", name="SMTP Outreach Test", description="Test", parameters_schema={}, allowed_agents=["*"]))
    invocation = ToolInvocation(
        tool_id="smtp_outreach",
        input_data={
            "target_email": "invalid-email",
            "subject": "Test Subject",
            "html_body": "Test Body"
        }
    )
    result = tool.execute(invocation)
    assert result["status"] == "error"
    assert "Invalid or malformed target email" in result["reason"]

def test_html_body_compliance_unsubscribe(setup_outreach_test_env):
    """Test that unsubscribe link is added if missing."""
    tool = SMTPOutreachTool(ToolConfig(tool_id="smtp_outreach_test", name="SMTP Outreach Test", description="Test", parameters_schema={}, allowed_agents=["*"]))
    invocation = ToolInvocation(
        tool_id="smtp_outreach",
        input_data={
            "target_email": "test@example.com",
            "subject": "Test Subject",
            "html_body": "This is a test email."
        }
    )
    # Mock SMTP to prevent actual sending but allow checking processed email body
    with patch('smtplib.SMTP_SSL') as mock_smtp_ssl, patch('smtplib.SMTP') as mock_smtp:
        mock_instance = mock_smtp_ssl.return_value
        mock_instance.__enter__.return_value.sendmail.return_value = {}
        result = tool.execute(invocation)
        assert result["status"] == "success"
        
        # Verify sendmail was called and check the body
        args, kwargs = mock_instance.__enter__.return_value.sendmail.call_args
        sent_email_content = args[2]
        assert "click here to unsubscribe" in sent_email_content

def test_html_body_compliance_unsubscribe_already_present(setup_outreach_test_env):
    """Test that unsubscribe link is not added if already present."""
    tool = SMTPOutreachTool(ToolConfig(tool_id="smtp_outreach_test", name="SMTP Outreach Test", description="Test", parameters_schema={}, allowed_agents=["*"]))
    invocation = ToolInvocation(
        tool_id="smtp_outreach",
        input_data={
            "target_email": "test@example.com",
            "subject": "Test Subject",
            "html_body": "This is a test email with an existing <a href='UNSUB_LINK'>unsubscribe</a> link."
        }
    )
    # Mock SMTP to prevent actual sending but allow checking processed email body
    with patch('smtplib.SMTP_SSL') as mock_smtp_ssl, patch('smtplib.SMTP') as mock_smtp:
        mock_instance = mock_smtp_ssl.return_value
        mock_instance.__enter__.return_value.sendmail.return_value = {}
        result = tool.execute(invocation)
        assert result["status"] == "success"
        
        # Verify sendmail was called and check the body
        args, kwargs = mock_instance.__enter__.return_value.sendmail.call_args
        sent_email_content = args[2]
        assert "This is a test email with an existing" in sent_email_content
        assert "click here to unsubscribe" not in sent_email_content # Should not add a duplicate
