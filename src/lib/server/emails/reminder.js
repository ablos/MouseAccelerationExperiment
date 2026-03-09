export function reminderEmail(name, code, type, participantId)
{
    const firstName = name ? name.split(' ')[0].charAt(0).toUpperCase() + name.split(' ')[0].slice(1).toLowerCase() : 'there';

    const isAfternoon = type === 'afternoon';
    const heading = isAfternoon
        ? 'Last chance — complete your session today'
        : "Today is a session day";
    const body = isAfternoon
        ? "This is a reminder that today is a session day and you haven't completed your session yet. Please try to complete it before the end of the day."
        : "Today is a session day for your mouse acceleration study. Please complete your session at your earliest convenience.";

    return `
        <!DOCTYPE html>
        <html>
        <body style="margin:0;padding:0;background:#f4f4f5;font-family:sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
                <tr><td align="center">
                <table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;">

                    <!-- Header -->
                    <tr><td style="background:#18181b;padding:32px;text-align:center;">
                    <span style="color:#ffffff;font-size:20px;font-weight:600;">Mouse Acceleration Study</span>
                    </td></tr>

                    <!-- Body -->
                    <tr><td style="padding:32px;">
                    <p style="margin:0 0 16px;color:#18181b;font-size:16px;">Hi ${firstName},</p>
                    <p style="margin:0 0 24px;color:#52525b;font-size:15px;line-height:1.6;">
                        ${body}
                    </p>

                    <!-- Code -->
                    <div style="background:#f4f4f5;border-radius:8px;padding:24px;text-align:center;margin:0 0 24px;">
                        <p style="margin:0 0 8px;color:#71717a;font-size:12px;text-transform:uppercase;letter-spacing:0.1em;">Your participant code</p>
                        <span style="font-family:monospace;font-size:36px;font-weight:700;color:#18181b;letter-spacing:0.15em;">${code}</span>
                    </div>

                    <!-- CTA -->
                    <div style="text-align:center;">
                        <a href="https://experiment.ablos.nl" style="background:#18181b;color:#ffffff;text-decoration:none;padding:12px 32px;border-radius:6px;font-size:15px;font-weight:500;display:inline-block;">
                        Go to the study
                        </a>
                    </div>
                    </td></tr>

                    <!-- Footer -->
                    <tr><td style="padding:16px 32px;border-top:1px solid #f4f4f5;text-align:center;">
                    <p style="margin:0;color:#a1a1aa;font-size:12px;">
                        This reminder was sent by students at Utrecht University.<br>
                        <a href="https://experiment.ablos.nl/api/unsubscribe?id=${participantId}&code=${code}" style="color:#a1a1aa;">Unsubscribe from reminders</a>
                    </p>
                    </td></tr>

                </table>
                </td></tr>
            </table>
        </body>
        </html>
    `;
}
