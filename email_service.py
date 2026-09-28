import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import html
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Auto-load .env file if it exists
env_path = os.path.join(CURRENT_DIR, ".env")
if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass

# Credentials
GMAIL_USER = os.environ.get("GMAIL_USER", "haseebrehman3460@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")

LOGO_ICON_PATH = os.path.join(CURRENT_DIR, "images", "logo-icon.png")

def get_admin_html(fname: str, lname: str, phone: str, email: str, message: str) -> str:
    clean_fname = html.escape(fname)
    clean_lname = html.escape(lname)
    clean_phone = html.escape(phone)
    clean_email = html.escape(email)
    clean_msg = html.escape(message).replace("\n", "<br>")
    
    wa_phone = "".join([c for c in phone if c.isdigit()])
    
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>New Project Inquiry</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0b0b; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f0f0f0;">
  <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #0b0b0b; padding: 40px 15px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; background-color: #141414; border: 1px solid #282828; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.6);">
          <!-- Header -->
          <tr>
            <td style="padding: 35px 35px 25px; background: linear-gradient(135deg, #1c1c1c 0%, #141414 100%); border-bottom: 1px solid #282828;">
              <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td>
                    <h1 style="margin: 0 0 5px; font-size: 24px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">New Project Inquiry</h1>
                    <p style="margin: 0; font-size: 14px; color: #a0a0a0;">Received from your website contact form</p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Client Details -->
          <tr>
            <td style="padding: 30px 35px;">
              <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 25px;">
                <tr>
                  <td style="padding: 12px 16px; background-color: #1c1c1c; border-radius: 10px; border: 1px solid #282828;">
                    <span style="display: block; font-size: 11px; text-transform: uppercase; color: #888888; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 4px;">Client Name</span>
                    <span style="font-size: 16px; font-weight: 700; color: #ffffff;">{clean_fname} {clean_lname}</span>
                  </td>
                </tr>
                <tr><td height="12"></td></tr>
                <tr>
                  <td style="padding: 12px 16px; background-color: #1c1c1c; border-radius: 10px; border: 1px solid #282828;">
                    <span style="display: block; font-size: 11px; text-transform: uppercase; color: #888888; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 4px;">Email Address</span>
                    <a href="mailto:{clean_email}" style="font-size: 15px; font-weight: 600; color: #FF5E14; text-decoration: none;">{clean_email}</a>
                  </td>
                </tr>
                <tr><td height="12"></td></tr>
                <tr>
                  <td style="padding: 12px 16px; background-color: #1c1c1c; border-radius: 10px; border: 1px solid #282828;">
                    <span style="display: block; font-size: 11px; text-transform: uppercase; color: #888888; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 4px;">Phone / WhatsApp</span>
                    <a href="tel:{clean_phone}" style="font-size: 15px; font-weight: 600; color: #ffffff; text-decoration: none;">{clean_phone}</a>
                  </td>
                </tr>
              </table>

              <!-- Message Box -->
              <div style="background-color: #1a1a1a; border-left: 4px solid #FF5E14; padding: 20px; border-radius: 0 10px 10px 0; border: 1px solid #282828; border-left: 4px solid #FF5E14;">
                <span style="display: block; font-size: 11px; text-transform: uppercase; color: #888888; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 8px;">Project Message</span>
                <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #e0e0e0;">{clean_msg if clean_msg else '<em>No additional message provided</em>'}</p>
              </div>

              <!-- Quick Action Buttons -->
              <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-top: 30px;">
                <tr>
                  <td align="center">
                    <a href="mailto:{clean_email}?subject=Re:%20Your%20Project%20Inquiry%20-%20Haseeb%20Rehman" style="display: inline-block; background-color: #FF5E14; color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-size: 14px; font-weight: 700; box-shadow: 0 4px 15px rgba(255, 94, 20, 0.4); margin-right: 10px; margin-bottom: 10px;">Reply to Client</a>
                    {f'<a href="https://wa.me/{wa_phone}" target="_blank" style="display: inline-block; background-color: #222222; color: #25D366; text-decoration: none; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 700; border: 1px solid #333333; margin-bottom: 10px;">Open in WhatsApp</a>' if wa_phone else ''}
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 20px 35px; background-color: #0f0f0f; border-top: 1px solid #222222; text-align: center;">
              <p style="margin: 0; font-size: 12px; color: #666666;">Haseeb Rehman Portfolio &bull; Automated Lead Notification</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def get_user_html(fname: str, lname: str, phone: str, email: str, message: str) -> str:
    clean_fname = html.escape(fname)
    clean_msg = html.escape(message).replace("\n", "<br>")
    
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Thank You for Contacting Haseeb Rehman</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0b0b; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f0f0f0;">
  <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #0b0b0b; padding: 40px 15px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; background-color: #141414; border: 1px solid #282828; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.6);">
          
          <!-- Top Accent Bar -->
          <tr>
            <td height="4" style="background: linear-gradient(90deg, #FF5E14 0%, #FF8A00 100%);"></td>
          </tr>

          <!-- Header with Inline Attached Logo -->
          <tr>
            <td style="padding: 35px 35px 25px; text-align: center; border-bottom: 1px solid #242424;">
              <table role="presentation" border="0" cellspacing="0" cellpadding="0" align="center">
                <tr>
                  <td style="vertical-align: middle; padding-right: 8px;">
                    <img src="cid:logo_icon" width="34" height="34" alt="" style="display: block; width: 34px; height: 34px; border: 0;">
                  </td>
                  <td style="vertical-align: middle;">
                    <span style="font-size: 28px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; display: inline-block; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">Haseeb<span style="color: #FF5E14;">.</span></span>
                  </td>
                </tr>
              </table>
              <span style="display: block; font-size: 13px; color: #888888; margin-top: 6px; font-weight: 600; letter-spacing: 0.5px;">Senior Full-Stack Web Developer</span>
            </td>
          </tr>

          <!-- Body Content -->
          <tr>
            <td style="padding: 35px 35px 25px;">
              <h2 style="margin: 0 0 16px; font-size: 22px; font-weight: 700; color: #ffffff;">Hi {clean_fname},</h2>
              
              <p style="margin: 0 0 18px; font-size: 15px; line-height: 1.6; color: #d0d0d0;">
                Thank you for reaching out! I have received your message and appreciate you considering me for your project.
              </p>
              
              <p style="margin: 0 0 25px; font-size: 15px; line-height: 1.6; color: #d0d0d0;">
                I am currently reviewing your details and will get back to you within <strong style="color: #FF5E14;">24 hours</strong> with insights, pricing, and next steps to bring your vision to life.
              </p>

              <!-- Message Summary Box -->
              {f'''
              <div style="background-color: #1a1a1a; border-radius: 12px; padding: 18px 20px; border: 1px solid #282828; margin-bottom: 28px;">
                <span style="display: block; font-size: 11px; text-transform: uppercase; color: #888888; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 6px;">Your Inquiry Summary:</span>
                <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #bbbbbb; font-style: italic;">"{clean_msg}"</p>
              </div>
              ''' if clean_msg else ''}

              <!-- Direct Connect CTA -->
              <div style="background: linear-gradient(135deg, rgba(255,94,20,0.08) 0%, rgba(255,94,20,0.02) 100%); border: 1px solid rgba(255,94,20,0.25); border-radius: 12px; padding: 22px; text-align: center; margin-bottom: 25px;">
                <p style="margin: 0 0 14px; font-size: 14px; color: #ffffff; font-weight: 600;">Need an urgent or immediate discussion?</p>
                <a href="https://wa.me/923268795099" target="_blank" style="display: inline-block; background-color: #FF5E14; color: #ffffff; text-decoration: none; padding: 12px 26px; border-radius: 8px; font-size: 14px; font-weight: 700; box-shadow: 0 4px 15px rgba(255, 94, 20, 0.4);">Chat on WhatsApp &rarr;</a>
              </div>

              <p style="margin: 0 0 5px; font-size: 14px; color: #aaaaaa;">Warm regards,</p>
              <p style="margin: 0; font-size: 16px; font-weight: 700; color: #ffffff;">Haseeb Rehman</p>
              <p style="margin: 3px 0 0; font-size: 12px; color: #888888; font-weight: 500;">Senior Full-Stack Web Developer</p>
            </td>
          </tr>

          <!-- Footer with Social Icons -->
          <tr>
            <td style="padding: 24px 35px; background-color: #0f0f0f; border-top: 1px solid #222222; text-align: center;">
              <table role="presentation" border="0" cellspacing="0" cellpadding="0" align="center" style="margin-bottom: 14px;">
                <tr>
                  <!-- GitHub Icon -->
                  <td style="padding: 0 8px;">
                    <a href="https://github.com/HasebRehman" target="_blank" title="GitHub" style="display: inline-block; width: 38px; height: 38px; line-height: 38px; background-color: #1a1a1a; border: 1px solid #2e2e2e; border-radius: 50%; text-align: center; text-decoration: none;">
                      <img src="https://img.icons8.com/material-outlined/48/ffffff/github.png" width="18" height="18" alt="GitHub" style="vertical-align: middle; display: inline-block; margin-top: -2px;">
                    </a>
                  </td>
                  <!-- LinkedIn Icon -->
                  <td style="padding: 0 8px;">
                    <a href="https://www.linkedin.com/in/haseebrehmanweb/" target="_blank" title="LinkedIn" style="display: inline-block; width: 38px; height: 38px; line-height: 38px; background-color: #1a1a1a; border: 1px solid #2e2e2e; border-radius: 50%; text-align: center; text-decoration: none;">
                      <img src="https://img.icons8.com/material-outlined/48/0A66C2/linkedin--v1.png" width="18" height="18" alt="LinkedIn" style="vertical-align: middle; display: inline-block; margin-top: -2px;">
                    </a>
                  </td>
                  <!-- WhatsApp Icon -->
                  <td style="padding: 0 8px;">
                    <a href="https://wa.me/923268795099" target="_blank" title="WhatsApp" style="display: inline-block; width: 38px; height: 38px; line-height: 38px; background-color: #1a1a1a; border: 1px solid #2e2e2e; border-radius: 50%; text-align: center; text-decoration: none;">
                      <img src="https://img.icons8.com/material-outlined/48/25D366/whatsapp--v1.png" width="18" height="18" alt="WhatsApp" style="vertical-align: middle; display: inline-block; margin-top: -2px;">
                    </a>
                  </td>
                </tr>
              </table>
              <p style="margin: 0; font-size: 11px; color: #555555;">&copy; 2026 Haseeb Rehman. All rights reserved.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_contact_emails(fname: str, lname: str, phone: str, email: str, message: str) -> tuple[bool, str]:
    """
    Sends two emails:
    1. Notification to Haseeb Rehman (haseebrehman3460@gmail.com)
    2. Auto-responder confirmation to the client (email) with inline CID logo image
    """
    if not email or not fname:
        return False, "Missing required fields (First Name and Email are required)."

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)

        # 1. Email to Haseeb (Admin Lead)
        admin_msg = MIMEMultipart("alternative")
        admin_msg["Subject"] = f"🚀 New Project Inquiry from {fname} {lname}"
        admin_msg["From"] = f"Haseeb Rehman Portfolio <{GMAIL_USER}>"
        admin_msg["To"] = GMAIL_USER
        admin_msg["Reply-To"] = email
        admin_html = get_admin_html(fname, lname, phone, email, message)
        admin_msg.attach(MIMEText(admin_html, "html"))
        server.sendmail(GMAIL_USER, [GMAIL_USER], admin_msg.as_string())

        # 2. Email to User (Auto-Responder) with RFC-2387 Related CID Attachment
        user_msg = MIMEMultipart("related")
        user_msg["Subject"] = "Thank you for reaching out! — Haseeb Rehman"
        user_msg["From"] = f"Haseeb Rehman <{GMAIL_USER}>"
        user_msg["To"] = email
        user_msg["Reply-To"] = GMAIL_USER

        user_alt = MIMEMultipart("alternative")
        user_msg.attach(user_alt)

        user_html = get_user_html(fname, lname, phone, email, message)
        user_alt.attach(MIMEText(user_html, "html"))

        # Attach logo icon as inline image (CID)
        if os.path.exists(LOGO_ICON_PATH):
            with open(LOGO_ICON_PATH, "rb") as img_f:
                logo_part = MIMEImage(img_f.read(), name="logo-icon.png")
                logo_part.add_header("Content-ID", "<logo_icon>")
                logo_part.add_header("Content-Disposition", "inline", filename="logo-icon.png")
                user_msg.attach(logo_part)

        server.sendmail(GMAIL_USER, [email], user_msg.as_string())

        server.quit()
        return True, "Emails sent successfully!"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
