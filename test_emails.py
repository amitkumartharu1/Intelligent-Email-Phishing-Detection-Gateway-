"""
test_emails.py - Send phishing and legitimate test emails to MailHog.

Phishing emails (should score HIGH / CRITICAL):
  1. Chase Bank credential harvest
  2. Amazon order confirmation scam
  3. Netflix account suspension
  4. DHL package delivery with malicious link
  5. GoPhish-style template with placeholders

Legitimate emails (should score SAFE / LOW):
  6. Internal team standup invite
  7. GitHub pull request notification
  8. Invoice from accounting
  9. Password reset from admin (legitimate)
 10. Newsletter / company announcement
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send(frm, to, subject, body_text, body_html, reply_to=None):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = frm
    msg["To"] = to
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))
    with smtplib.SMTP("localhost", 1025) as s:
        s.sendmail(frm, [to], msg.as_string())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PHISHING EMAILS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("Sending phishing test emails...")

# ── P1: Chase Bank credential harvest ────────────────────────
send(
    frm="alerts@chase-secure-banking.net",
    to="admin@ipedg.local",
    reply_to="noreply@chase-helpdesk.ru",
    subject="URGENT: Your Chase Bank Account Has Been Locked",
    body_text=(
        "Dear Chase Customer,\n\n"
        "We detected unauthorized access to your Chase bank account from an unknown device.\n\n"
        "Your account has been locked. Account will be suspended permanently within 24 hours "
        "unless you verify your identity immediately.\n\n"
        "Click here to unlock: http://chase-secure-banking.net/unlock?token=9f3kx2\n\n"
        "Do not ignore this message. Act immediately to avoid permanent account closure.\n\n"
        "Chase Bank Security Team\n"
    ),
    body_html=(
        "<html><body>"
        "<h2>Your Account Has Been Locked</h2>"
        "<p>We detected <b>unauthorized access</b> to your Chase bank account.</p>"
        "<p>Your account will be <b>suspended permanently</b> within 24 hours.</p>"
        '<p><a href="http://chase-secure-banking.net/unlock?token=9f3kx2">Unlock My Account Now</a></p>'
        "<p>Act immediately to avoid suspension.</p>"
        "</body></html>"
    ),
)
print("  [P1] Chase Bank credential harvest - SENT")

# ── P2: Amazon order scam ─────────────────────────────────────
send(
    frm="order-confirm@amazon-orders-verify.xyz",
    to="admin@ipedg.local",
    reply_to="support@amazon-helpdesk.cc",
    subject="Your Amazon Order #114-8293847 Has Been Placed - Verify Payment",
    body_text=(
        "Dear Amazon Customer,\n\n"
        "Your order has been placed but your payment could not be verified.\n\n"
        "Order #114-8293847 | Total: $329.99\n\n"
        "Your account will be suspended if you do not verify your payment details immediately.\n\n"
        "Verify payment: http://amazon-orders-verify.xyz/payment?order=114-8293847&token=zx99k\n\n"
        "If you did not place this order, verify your account immediately to avoid unauthorized charges.\n\n"
        "Amazon Customer Service\n"
    ),
    body_html=(
        "<html><body>"
        "<h2>Payment Verification Required</h2>"
        "<p>Your Amazon order payment could not be verified.</p>"
        "<p><b>Order #114-8293847</b> | Total: <b>$329.99</b></p>"
        "<p>Your account has been limited. Verify your payment details to avoid account suspension.</p>"
        '<p><a href="http://amazon-orders-verify.xyz/payment?order=114-8293847&token=zx99k">'
        "Verify Payment Now</a></p>"
        "</body></html>"
    ),
)
print("  [P2] Amazon payment scam - SENT")

# ── P3: Netflix account suspension ───────────────────────────
send(
    frm="billing@netflix-account-verify.com",
    to="admin@ipedg.local",
    reply_to="noreply@netflix-support.info",
    subject="Netflix: Your Account Will Be Suspended - Update Billing Now",
    body_text=(
        "Dear Netflix Member,\n\n"
        "We were unable to process your payment for your Netflix subscription.\n\n"
        "Your account will be suspended within 24 hours unless you update your billing information.\n\n"
        "Update billing: http://netflix-account-verify.com/billing?uid=92kxp&token=verify\n\n"
        "Do not ignore this message. Verify your account to avoid losing access to Netflix.\n\n"
        "Act immediately or face permanent account closure.\n\n"
        "Netflix Support Team\n"
    ),
    body_html=(
        "<html><body>"
        "<h2>Your Netflix Account Will Be Suspended</h2>"
        "<p>We could not process your Netflix payment.</p>"
        "<p>Your account will be <b>permanently closed</b> in 24 hours.</p>"
        '<p><a href="http://netflix-account-verify.com/billing?uid=92kxp&token=verify">'
        "Update Billing Information</a></p>"
        "<p>Act immediately to avoid losing your account.</p>"
        "</body></html>"
    ),
)
print("  [P3] Netflix billing scam - SENT")

# ── P4: DHL package phishing ──────────────────────────────────
send(
    frm="delivery@dhl-parcel-tracking.xyz",
    to="admin@ipedg.local",
    reply_to="noreply@dhl-helpdesk.ru",
    subject="DHL: Your Package Could Not Be Delivered - Action Required",
    body_text=(
        "Dear Customer,\n\n"
        "Your DHL package (Tracking: 1234567890) could not be delivered due to an incorrect address.\n\n"
        "To reschedule your delivery, you must pay a small redelivery fee of $2.99 within 24 hours.\n\n"
        "Pay redelivery fee: http://dhl-parcel-tracking.xyz/redeliver?id=1234567890&fee=2.99\n\n"
        "Failure to pay within 24 hours will result in your package being returned to the sender.\n\n"
        "Your account will be suspended if payment is not received.\n\n"
        "DHL Express Customer Service\n"
    ),
    body_html=(
        "<html><body>"
        "<h2>Package Delivery Failed</h2>"
        "<p>Your DHL package could not be delivered.</p>"
        "<p>Tracking: <b>1234567890</b></p>"
        "<p>Pay redelivery fee to avoid package return and account suspension.</p>"
        '<p><a href="http://dhl-parcel-tracking.xyz/redeliver?id=1234567890&fee=2.99">'
        "Pay $2.99 Redelivery Fee</a></p>"
        "<p>Act immediately - package will be returned in 24 hours.</p>"
        "</body></html>"
    ),
)
print("  [P4] DHL delivery scam - SENT")

# ── P5: GoPhish-style template ────────────────────────────────
send(
    frm="it-security@ipedg-helpdesk.net",
    to="admin@ipedg.local",
    reply_to="noreply@helpdesk-verify.xyz",
    subject="IT Security Alert: Your Account Password Has Expired",
    body_text=(
        "Dear {{.FirstName}},\n\n"
        "Your IT account password has expired and your account will be locked within 2 hours.\n\n"
        "Please click the link below to reset your password immediately:\n"
        "{{.URL}}\n\n"
        "If you do not reset your password, your account will be suspended.\n\n"
        "Do not share this link with anyone. Act immediately.\n\n"
        "IT Security Team\n"
        "{{.Tracker}}\n"
    ),
    body_html=(
        "<html><body>"
        "<h2>Password Expiry Notice</h2>"
        "<p>Dear {{.FirstName}},</p>"
        "<p>Your account password has expired. Your account will be <b>locked</b> in 2 hours.</p>"
        '<p><a href="{{.URL}}">Reset Password Now</a></p>'
        "<p>Act immediately to avoid being locked out.</p>"
        "<img src='{{.Tracker}}' width='1' height='1'>"
        "</body></html>"
    ),
)
print("  [P5] GoPhish template (placeholders) - SENT")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LEGITIMATE EMAILS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\nSending legitimate test emails...")

# ── L1: Internal team standup ─────────────────────────────────
send(
    frm="alice@ipedg.local",
    to="admin@ipedg.local",
    subject="Daily Standup - Monday 10:00 AM",
    body_text=(
        "Hi team,\n\n"
        "Just a reminder that our daily standup is at 10:00 AM today.\n\n"
        "Agenda:\n"
        "- Sprint progress update\n"
        "- Blocker review\n"
        "- Q3 planning discussion\n\n"
        "Meeting link: https://meet.google.com/xyz-abc-123\n\n"
        "See you there!\n\n"
        "Alice\n"
    ),
    body_html=(
        "<html><body>"
        "<p>Hi team,</p>"
        "<p>Daily standup at <b>10:00 AM</b> today.</p>"
        "<ul><li>Sprint progress</li><li>Blockers</li><li>Q3 planning</li></ul>"
        '<p><a href="https://meet.google.com/xyz-abc-123">Join Meeting</a></p>'
        "<p>Alice</p>"
        "</body></html>"
    ),
)
print("  [L1] Internal standup invite - SENT")

# ── L2: GitHub pull request notification ─────────────────────
send(
    frm="notifications@github.com",
    to="admin@ipedg.local",
    subject="[phishing-email-detection-system] Pull request: Fix scoring pipeline (#42)",
    body_text=(
        "Bob opened a pull request in your repository phishing-email-detection-system.\n\n"
        "Title: Fix scoring pipeline\n"
        "Branch: fix/scoring-pipeline\n\n"
        "Changes:\n"
        "- Updated decision_engine.py weighting logic\n"
        "- Added rule high-confidence floor\n"
        "- Fixed API zero-score dilution issue\n\n"
        "View pull request: https://github.com/yourorg/phishing-email-detection-system/pull/42\n\n"
        "---\n"
        "You are receiving this because you are subscribed to this repository.\n"
        "Unsubscribe: https://github.com/notifications/unsubscribe-auth/xyz\n"
    ),
    body_html=(
        "<html><body>"
        "<p>Bob opened pull request <b>#42</b> in phishing-email-detection-system.</p>"
        "<p><b>Fix scoring pipeline</b></p>"
        '<p><a href="https://github.com/yourorg/phishing-email-detection-system/pull/42">View Pull Request</a></p>'
        "<p>You are subscribed to this repository.</p>"
        "</body></html>"
    ),
)
print("  [L2] GitHub PR notification - SENT")

# ── L3: Invoice from accounting ───────────────────────────────
send(
    frm="accounting@ipedg.local",
    to="admin@ipedg.local",
    subject="Invoice #INV-2024-089 - Monthly Software Licenses",
    body_text=(
        "Hi,\n\n"
        "Please find attached invoice #INV-2024-089 for monthly software licenses.\n\n"
        "Invoice Details:\n"
        "  Item: Software License Renewal - April 2024\n"
        "  Amount: $1,250.00\n"
        "  Due Date: April 30, 2024\n"
        "  Payment Method: Bank Transfer\n\n"
        "Account Details:\n"
        "  Bank: First National Bank\n"
        "  Account Name: IPEDG Ltd\n"
        "  Reference: INV-2024-089\n\n"
        "Please process payment by the due date.\n\n"
        "Best regards,\n"
        "Finance Team\n"
        "IPEDG Ltd\n"
    ),
    body_html=(
        "<html><body>"
        "<h2>Invoice #INV-2024-089</h2>"
        "<table border='1'>"
        "<tr><td>Item</td><td>Software License Renewal</td></tr>"
        "<tr><td>Amount</td><td>$1,250.00</td></tr>"
        "<tr><td>Due Date</td><td>April 30, 2024</td></tr>"
        "</table>"
        "<p>Please process payment by the due date.</p>"
        "<p>Finance Team, IPEDG Ltd</p>"
        "</body></html>"
    ),
)
print("  [L3] Accounting invoice - SENT")

# ── L4: Password reset (legitimate, from internal system) ─────
send(
    frm="noreply@ipedg.local",
    to="admin@ipedg.local",
    subject="Password Reset Request for admin@ipedg.local",
    body_text=(
        "Hello,\n\n"
        "We received a password reset request for your account admin@ipedg.local.\n\n"
        "If you made this request, use the link below to reset your password.\n"
        "This link will expire in 30 minutes.\n\n"
        "Reset link: http://localhost:5000/auth/reset-password?token=local_reset_abc123\n\n"
        "If you did not request a password reset, please ignore this email.\n"
        "Your password will not be changed.\n\n"
        "IPEDG Security Team\n"
    ),
    body_html=(
        "<html><body>"
        "<p>Hello,</p>"
        "<p>Password reset requested for <b>admin@ipedg.local</b>.</p>"
        '<p><a href="http://localhost:5000/auth/reset-password?token=local_reset_abc123">'
        "Reset My Password</a></p>"
        "<p>This link expires in 30 minutes. If you did not request this, ignore this email.</p>"
        "<p>IPEDG Security Team</p>"
        "</body></html>"
    ),
)
print("  [L4] Legitimate password reset - SENT")

# ── L5: Company newsletter ────────────────────────────────────
send(
    frm="hr@ipedg.local",
    to="admin@ipedg.local",
    subject="IPEDG Monthly Newsletter - April 2024",
    body_text=(
        "Hello Team,\n\n"
        "Welcome to the April 2024 edition of the IPEDG newsletter.\n\n"
        "Highlights this month:\n\n"
        "1. New team members\n"
        "   We welcome three new engineers joining the platform team.\n\n"
        "2. Q1 results\n"
        "   We exceeded our targets by 12 percent. Great work, everyone!\n\n"
        "3. Upcoming events\n"
        "   - Team lunch: April 18th, 12:30 PM\n"
        "   - Quarterly review: April 25th, 2:00 PM\n\n"
        "4. Policy update\n"
        "   The updated remote work policy is now available on the internal wiki.\n\n"
        "Have a great month!\n\n"
        "HR Team\n"
        "IPEDG Ltd\n"
    ),
    body_html=(
        "<html><body>"
        "<h1>IPEDG Monthly Newsletter - April 2024</h1>"
        "<h3>New Team Members</h3><p>Three new engineers joining the platform team.</p>"
        "<h3>Q1 Results</h3><p>Exceeded targets by 12%. Great work!</p>"
        "<h3>Upcoming Events</h3>"
        "<ul><li>Team lunch: April 18th</li><li>Quarterly review: April 25th</li></ul>"
        "<p>Have a great month! - HR Team</p>"
        "</body></html>"
    ),
)
print("  [L5] Company newsletter - SENT")

print("\nAll 10 test emails sent successfully!")
print("\nExpected results:")
print("  PHISHING  -> HIGH or CRITICAL risk:")
print("    P1 Chase Bank    - brand + mismatch + keywords + suspicious URL")
print("    P2 Amazon scam   - brand + mismatch + keywords + suspicious URL")
print("    P3 Netflix scam  - brand + mismatch + CTA + suspension language")
print("    P4 DHL scam      - brand + mismatch + urgency + suspicious URL")
print("    P5 GoPhish       - unresolved placeholders + brand + CTA")
print()
print("  LEGITIMATE -> SAFE or LOW risk:")
print("    L1 Standup       - internal sender, no threat signals")
print("    L2 GitHub PR     - known service domain, informational")
print("    L3 Invoice       - internal sender, no URL threats")
print("    L4 Password reset- internal system, localhost URL")
print("    L5 Newsletter    - internal sender, no threat signals")
